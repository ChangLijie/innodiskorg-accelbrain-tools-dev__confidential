"""
author: Jay
version: 1.0
licence: MIT
"""

import httpx
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        API_BASE_URL: str = Field(
            default="http://172.16.92.144",
            description="Base URL for accessing iVIT-T endpoints.",
        )
        API_PORT: str = Field(
            default="6530",
            description="Port for accessing iVIT-T endpoints.",
        )
        API_ROUTER: str = Field(
            default="get_all_project",
            description="Router for accessing iVIT-T endpoints.",
        )

    def __init__(self):
        self.valves = self.Valves()

    def get_ivit_project(self) -> str:
        """
        Get all projects from iVIT-T.

        :return: A string covert form dictionary that containing project information or an error message.
        """
        url = f"{self.valves.API_BASE_URL}:{self.valves.API_PORT}/{self.valves.API_ROUTER}"

        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            projects = data.get("data", {})
            if not projects:
                return {"message": "No project in iVIT", "projects": []}

            print(projects)
            return str(projects)

        except httpx.RequestError as e:
            return {"error": f"Failed to call API: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e}"}
        except KeyError:
            return {"error": "Response format error"}

    def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """

        # Do not include :param for __user__ in the docstring as it should not be shown in the tool's specification
        # The session user object will be passed as a parameter when the function is called

        print(__user__)
        result = ""

        if "name" in __user__:
            result += f"User: {__user__['name']}"
        if "id" in __user__:
            result += f" (ID: {__user__['id']})"
        if "email" in __user__:
            result += f" (Email: {__user__['email']})"

        if result == "":
            result = "User: Unknown"

        return result


# 測試用
if __name__ == "__main__":
    tools = Tools()
    print(tools.get_ivit_project())
