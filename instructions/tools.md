# Best Practices for Creating LLM Tools: A PRD

This document outlines best practices for designing and implementing tools for use with Large Language Models (LLMs), aiming to ensure their effectiveness and maintainability.

## 1. Tool Design Principles

### Clarity and Specificity

Tool names and descriptions should be clear, concise, and accurately reflect the tool's function. For instance, instead of a vague "Reddit tool," use specific names like "Read Reddit Posts" or "Post to Subreddit." This approach aids the LLM in understanding and selecting the appropriate tool.

### Present Tense and Succinct Tone

Use the present tense in tool descriptions to align with the operational context of LLMs. Keep descriptions succinct and avoid unnecessary verbosity. For example: "This tool retrieves the weather forecast for a given location."

### Robust Input Handling

LLMs can sometimes generate outputs with missing or unexpected elements. Tools should be resilient to such variations by:

- Setting default values for parameters.
- Utilizing flexible input mechanisms to handle extra arguments without crashing.
- Providing feedback to the LLM when inputs are invalid or incomplete.

### Output Formatting

Tailor tool outputs to be easily interpretable by the LLM. Avoid returning raw data formats like HTML. Structure the output in a clear and concise manner, possibly using JSON or similar formats.

### Error Handling and Feedback

Implement robust error handling within tools to gracefully manage unexpected situations. Provide informative feedback to the LLM, enabling it to understand the error and potentially take corrective actions.

## 2. Tool Categorization

Group tools into categories based on their primary function, making it easier to manage and select them:

1. **Data Getters**: Tools that retrieve information.

   - Examples: API wrappers for databases, web scrapers, search engines, RAG systems.

2. **Data Manipulators**: Tools that process and transform data.

   - Examples: Code interpreters, data format converters, math solvers.

3. **Action Takers**: Tools that perform actions.

   - Examples: Sending emails, writing to files, interacting with external systems, controlling robotic arms.

4. **Verification Checkers**: Tools that validate data.
   - Examples: Input validation functions, code checkers, logical reasoning engines.

## 3. Tool Implementation

### Frameworks and Libraries

Utilize appropriate frameworks and libraries to facilitate tool development:

- **Pydantic**: For defining data models and validating inputs with type hints and constraints.

  ```python
  from pydantic import BaseModel, Field

  class WeatherQuery(BaseModel):
      location: str = Field(..., description="The city and country for the weather forecast")
      days: int = Field(default=1, ge=1, le=7, description="Number of days for the forecast (1-7)")
  ```

### Tool Structure

When creating tools for LLMs, consider the following structure:

1. **Input Schema**: Use Pydantic models to define and validate input parameters.
2. **Tool Class**: Create a class that encapsulates the tool's functionality.
3. **Run Method**: Implement a method (e.g., `run`) that takes the validated input and performs the tool's main function.
4. **Error Handling**: Implement comprehensive error handling and provide informative feedback.
5. **Output Formatting**: Return structured data that's easy for the LLM to interpret.

### Example Implementation

Here's an example of a weather forecast tool implementation following these best practices:

```python
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class WeatherQuery(BaseModel):
    location: str = Field(..., description="The city and country for the weather forecast")
    days: Optional[int] = Field(default=1, ge=1, le=7, description="Number of days for the forecast (1-7)")

class WeatherTool:
    name = "get_weather_forecast"
    description = "Retrieves the weather forecast for a given location and number of days"

    @staticmethod
    def run(query: WeatherQuery) -> Dict[str, Any]:
        """
        Retrieves the weather forecast for a given location and number of days.

        Args:
            query (WeatherQuery): The query parameters for the weather forecast.

        Returns:
            Dict[str, Any]: A dictionary containing the weather forecast data.

        Raises:
            ValueError: If the input parameters are invalid.
            RequestException: If there's an error fetching the weather data.
        """
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key:
            return {"error": "Weather API key not found in environment variables."}

        base_url = "http://api.weatherapi.com/v1/forecast.json"

        try:
            response = requests.get(
                base_url,
                params={
                    "key": api_key,
                    "q": query.location,
                    "days": query.days,
                }
            )
            response.raise_for_status()
            data = response.json()

            # Process and format the data
            location_name = data['location']['name']
            country = data['location']['country']
            forecast = []

            for day in data['forecast']['forecastday']:
                forecast.append({
                    "date": day['date'],
                    "max_temp_c": day['day']['maxtemp_c'],
                    "min_temp_c": day['day']['mintemp_c'],
                    "condition": day['day']['condition']['text']
                })

            return {
                "location": location_name,
                "country": country,
                "forecast": forecast
            }

        except requests.RequestException as e:
            return {"error": f"Error fetching weather data: {str(e)}"}
        except (KeyError, IndexError) as e:
            return {"error": f"Error processing weather data: {str(e)}"}

# Example usage
if __name__ == "__main__":
    weather_tool = WeatherTool()
    query = WeatherQuery(location="London,UK", days=3)
    result = weather_tool.run(query)
    print(result)
```

This example demonstrates:

- Clear naming and description
- Use of Pydantic for input validation
- Robust error handling
- Structured output formatting
- Use of environment variables for API keys

By following these best practices, you can create tools that are effective, maintainable, and easy for LLMs to use and understand.
