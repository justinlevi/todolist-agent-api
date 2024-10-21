# How to run this script:
# 1. Make sure you have the required libraries installed:
#    pip install openai qdrant-client pandas python-dotenv
# 2. Ensure your OpenAI API key is set in your .env file:
#    OPENAI_API_KEY="your-api-key-here"
# 3. Have a Qdrant server running locally on the default port (6333)
# 4. Run this script from the src directory:
#    python prep_data.py

import json
import os
import logging
from dotenv import load_dotenv
import markdown
from bs4 import BeautifulSoup
import tiktoken
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import asyncio
import time
import argparse
from pydantic import BaseModel, Field
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_SERVICE_API_KEY = os.getenv("QDRANT_SERVICE_API_KEY")

# print out the env variables
print(f"QDRANT_HOST: {QDRANT_HOST}")
print(f"QDRANT_SERVICE_API_KEY: {QDRANT_SERVICE_API_KEY}")

# Initialize Qdrant client
if QDRANT_SERVICE_API_KEY:
    qdrant = QdrantClient(
        host=QDRANT_HOST,
        api_key=QDRANT_SERVICE_API_KEY,
        prefer_grpc=False,
        verify=False,
        https=False,
    )
else:
    qdrant = QdrantClient(host=QDRANT_HOST, prefer_grpc=False, verify=False)

# Add this debug print statement
print(f"Attempting to connect to Qdrant at: {QDRANT_HOST}")

# Constants
COLLECTION_NAME = "procedures"
EMBEDDING_MODEL = "text-embedding-3-large"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class Tags(BaseModel):
    tags: List[str] = Field(..., description="List of tags")


def get_encoding(encoding_name):
    return tiktoken.get_encoding(encoding_name)


def split_text(text, chunk_size=500, chunk_overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # Find the last period or newline within the chunk
            last_break = max(text.rfind(".", start, end), text.rfind("\n", start, end))
            if last_break != -1:
                end = last_break + 1
        chunk = text[start:end].strip()
        chunks.append(chunk)
        start = end - chunk_overlap
    return chunks


def markdown_to_text(markdown_string):
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()


async def generate_consistent_tags(full_text):
    print("Generating consistent tags for the entire document...")
    start_time = time.time()

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-3.5-turbo-1106",  # Using a faster model with JSON output capability
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a medical tagging assistant. Generate 5 consistent tags that apply to the entire medical document. Respond with a JSON object containing a 'tags' array.",
            },
            {
                "role": "user",
                "content": f"Text: {full_text}\n\nGenerate consistent tags:",
            },
        ],
    )

    tags_json = json.loads(response.choices[0].message.content)
    consistent_tags = Tags(**tags_json).tags
    end_time = time.time()
    print(
        f"Consistent tags generated in {end_time - start_time:.2f} seconds: {consistent_tags}"
    )

    return consistent_tags


async def generate_specific_tags(text, consistent_tags):
    print(f"Generating specific tags for chunk: {text[:50]}...")
    start_time = time.time()

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-3.5-turbo-1106",  # Using a faster model with JSON output capability
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"You are a medical tagging assistant. Generate 3 specific tags for the given medical text chunk. These tags should be different from the consistent tags: {', '.join(consistent_tags)}. Respond with a JSON object containing a 'tags' array.",
            },
            {"role": "user", "content": f"Text: {text}\n\nGenerate specific tags:"},
        ],
    )

    tags_json = json.loads(response.choices[0].message.content)
    specific_tags = Tags(**tags_json).tags
    end_time = time.time()
    print(
        f"Specific tags generated in {end_time - start_time:.2f} seconds: {specific_tags}"
    )

    return specific_tags


async def process_markdown_files(data_directory):
    data = []
    for root, _, files in os.walk(data_directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                procedure_name = os.path.basename(os.path.dirname(file_path))
                file_type = os.path.splitext(file)[0]

                print(f"Processing file: {file_path}")
                with open(file_path, "r") as f:
                    markdown_content = f.read()

                # Split the content into chunks
                chunks = split_text(markdown_content)

                # Generate consistent tags for the entire document
                consistent_tags = await generate_consistent_tags(markdown_content)

                for i, chunk in enumerate(chunks):
                    print(f"Processing chunk {i+1}/{len(chunks)} for {file_path}")
                    specific_tags = await generate_specific_tags(chunk, consistent_tags)

                    data_item = {
                        "text": chunk,
                        "metadata": {
                            "procedure": procedure_name,
                            "type": file_type,
                            "chunk_index": i + 1,
                            "total_chunks": len(chunks),
                            "source_file": file_path,
                            "consistent_tags": consistent_tags,
                            "specific_tags": specific_tags,
                        },
                    }
                    data.append(data_item)

    return data


def get_all_points(client, collection_name):
    all_points = []
    offset = 0
    limit = 100  # You can adjust this based on your needs

    while True:
        response = client.scroll(
            collection_name=collection_name, limit=limit, offset=offset
        )
        all_points.extend(response[0])

        if len(response[0]) < limit:
            break

        offset += limit

    return all_points


async def main(action):
    if action == "generate":
        # Clear existing collection
        try:
            qdrant.delete_collection(collection_name=COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'")
        except Exception as e:
            print(f"No existing collection '{COLLECTION_NAME}' to delete")

        # Create new collection
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=rest.VectorParams(
                size=3072,  # Size for text-embedding-3-large
                distance=rest.Distance.COSINE,
            ),
        )
        print(f"Created new collection '{COLLECTION_NAME}'")

        # Process markdown files
        data_directory = "data"
        processed_data = await process_markdown_files(data_directory)
        print(f"Processed {len(processed_data)} chunks")

        # Create embeddings and upload to Qdrant
        for i, item in enumerate(processed_data):
            try:
                print(f"Creating embedding for item {i+1}/{len(processed_data)}")
                start_time = time.time()
                embedding = client.embeddings.create(
                    model=EMBEDDING_MODEL, input=item["text"]
                )
                vector = embedding.data[0].embedding
                end_time = time.time()
                print(f"Embedding created in {end_time - start_time:.2f} seconds")

                print(f"Uploading item {i+1}/{len(processed_data)} to Qdrant")
                start_time = time.time()
                qdrant.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[
                        rest.PointStruct(
                            id=i,
                            vector=vector,
                            payload={
                                "text": item["text"],
                                "metadata": item["metadata"],
                            },
                        )
                    ],
                )
                end_time = time.time()
                print(f"Item uploaded to Qdrant in {end_time - start_time:.2f} seconds")
            except Exception as e:
                print(f"Error processing item {i}: {e}")

    # Show all data (for both 'generate' and 'show' actions)
    print("Retrieving all points from Qdrant...")
    all_points = get_all_points(qdrant, COLLECTION_NAME)

    print("Data in Qdrant (excluding embeddings):")
    for point in all_points:
        print(f"ID: {point.id}")
        print(f"Text: {point.payload['text']}")
        print(f"Metadata: {point.payload['metadata']}")
        print("---")

    print(f"Total points in Qdrant: {len(all_points)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process markdown files and interact with Qdrant."
    )
    parser.add_argument(
        "action",
        choices=["generate", "show"],
        help="Action to perform: 'generate' to process files and upload to Qdrant, 'show' to display existing data",
    )
    args = parser.parse_args()

    asyncio.run(main(args.action))
