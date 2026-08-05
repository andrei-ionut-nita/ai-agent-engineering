"""
The second of Lesson 17's two servers: a fake, deterministic "weather"
server, no real API call needed for this lesson to make its point.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

_FAKE_FORECASTS = {
    "seattle": "Rainy, 55F",
    "phoenix": "Sunny, 95F",
}


@mcp.tool()
def get_forecast(city: str) -> str:
    """Get a short weather forecast for a city."""
    return _FAKE_FORECASTS.get(city.lower(), "No forecast available for that city.")


if __name__ == "__main__":
    mcp.run(transport="stdio")
