"""
author: Jay
version: 0.5.18
licence: MIT
"""

import ast
from typing import List

import httpx
from pydantic import BaseModel, Field


class TrainingParameter(BaseModel):
    training_method: str
    model: str
    batch_size: int
    step: int
    input_shape: List[int]


class TrainingConfig(BaseModel):
    project_uuid: str
    training_parameter: TrainingParameter


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

    def __init__(self):
        self.valves = self.Valves()

    def get_model(
        self,
        __model__: dict = {
            "id": "test",
            "name": "test",
            "object": "model",
            "created": 1741659012,
            "owned_by": "ollama",
            "info": {
                "id": "test",
                "user_id": "2441859e-19ea-4667-81bd-4ff5f4a92d51",
                "data_permission_level": 0,
                "base_model_id": "llama3.1:8b",
                "name": "test",
                "params": {},
                "meta": {
                    "profile_image_url": "/static/favicon.png",
                    "description": None,
                    "capabilities": {"vision": True, "citations": True},
                    "suggestion_prompts": None,
                    "tags": [],
                    "toolIds": ["sample"],
                },
                "access_control": {
                    "read": {"group_ids": [], "user_ids": []},
                    "write": {"group_ids": [], "user_ids": []},
                },
                "is_active": True,
                "updated_at": 1741659012,
                "created_at": 1741659012,
            },
            "preset": True,
            "actions": [],
        },
    ) -> dict:
        """
        Get model name
        """

        return __model__["info"]["base_model_id"]

    def get_model_list(self, project_uuid: str) -> list:
        """
        Get the available training models from project_uuid.

        :param project_uuid: The uuid of the project to get default training parameter for.
        :return: A list containing the available training models if successful, or an error message.
        """
        url = f"{self.valves.API_BASE_URL}:{self.valves.API_PORT}/{project_uuid}/get_model"

        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            projects = data.get("data", {})
            if not projects:
                return {"message": "No available model."}

            # print(projects)
            return str(projects["model"])

        except httpx.RequestError as e:
            return {"error": f"Failed to call API: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e}"}
        except KeyError:
            return {"error": "Response format error"}

    def get_default_training_parameter(self, project_uuid: str) -> dict:
        """
        Get default training parameter from project_uuid.
        :param project_uuid: The uuid of the project to get default training parameter for.
        :return: A dict containing the training parameter if successful, or an error message.
        """
        url = f"{self.valves.API_BASE_URL}:{self.valves.API_PORT}/{project_uuid}/get_default_param"
        json_data = {"training_method": "Quick Training"}
        try:
            response = httpx.post(url, json=json_data)
            response.raise_for_status()
            data = response.json()

            projects = data.get("data", {})
            if not projects:
                return {"message": "Can't get default training parameters."}

            # print(projects)
            return str(projects)

        except httpx.RequestError as e:
            return {"error": f"Failed to call API: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e}"}
        except KeyError:
            return {"error": "Response format error"}

    def get_ivit_project(self) -> str:
        """
        Get all projects from iVIT-T.

        :return: A string covert form dictionary that containing project information or an error message.
        """
        url = f"{self.valves.API_BASE_URL}:{self.valves.API_PORT}/get_all_project"

        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            projects = data.get("data", {})
            if not projects:
                return {"message": "No project in iVIT", "projects": []}

            # print(projects)
            return str(projects)

        except httpx.RequestError as e:
            return {"error": f"Failed to call API: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e}"}
        except KeyError:
            return {"error": "Response format error"}

    def training_new_iteration(
        self,
        project_name: str,
        batch_size: int,
        model: str,
        step: int,
        input_shape: List[int],
    ) -> str:
        """
        Initiates a new training iteration for the specified project in iVIT-T.

        :param project_name: The name of the project to start a new training iteration for.
        :param batch_size: The batch size for training.
        :param model: The model name (e.g., "ResNet50", "YOLOv5").

        :param step: The number of training steps.
        :param input_shape: The input shape of the model as a list [height, width, channels].
        :return: A string containing the task UUID if successful, or an error message.
        """
        url = f"{self.valves.API_BASE_URL}:{self.valves.API_PORT}/training_schedule"
        projects = ast.literal_eval(self.get_ivit_project())
        match_uuid = None
        for uuid, project in projects.items():
            if project["project_name"] == project_name:
                match_uuid = uuid

        if not match_uuid:
            return "Create training parameter get error! Failed to find project"

        default_parameter = ast.literal_eval(
            self.get_default_training_parameter(project_uuid=str(match_uuid))
        )

        available_model = ast.literal_eval(
            self.get_model_list(project_uuid=str(match_uuid))
        )
        try:
            batch_size = int(batch_size)
        except:
            batch_size = None

        try:
            model = str(batch_size)
        except:
            model = None

        try:
            step = int(step)
        except:
            step = None

        try:
            input_shape = ast.literal_eval(input_shape)
        except:
            input_shape = None

        if model not in available_model:
            model = default_parameter["training_param"]["model"]
            print(
                f"Model not support on the project {project_name}, Change model to {model}"
            )

        try:
            data = {
                "project_uuid": str(match_uuid),
                "training_parameter": {
                    "training_method": "Quick Training",
                    "model": model,
                    "batch_size": (
                        batch_size
                        if isinstance(batch_size, int) and batch_size > 0
                        else 1
                    ),
                    "step": (
                        step
                        if isinstance(step, int) and step > 0
                        else default_parameter["training_param"]["step"]
                    ),
                    "input_shape": (
                        input_shape
                        if isinstance(input_shape, list)
                        and len(input_shape) == 3
                        and all(isinstance(i, int) and i > 0 for i in input_shape)
                        else default_parameter["training_param"]["input_shape"]
                    ),
                },
            }
            training_config = TrainingConfig(**data)
        except:
            return "Create training parameter get error! So stop create new training task , please check!"
        json_data = training_config.model_dump()
        print(f"\n\n\n\n Training parameter : \n\n\n\n{data}\n\n\n\n")

        response = httpx.post(url, json=json_data)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("status") == 200:
                task_uuid = response_data["data"].get("task_uuid")
                print(
                    f"The training has been successfully submitted to iVIT-T. The generated Task UUID is {task_uuid}."
                )
                return f"The training has been successfully submitted to iVIT-T. The generated Task UUID is {task_uuid}."
            else:
                print(
                    f"Create training parameter get error! Request failed: {response_data.get('message')}"
                )
                return f"Create training parameter get error! Request failed: {response_data.get('message')}"
        else:
            print(
                f"Create training parameter get error! HTTP Error: {response.status_code}"
            )
            return f"Create training parameter get error!HTTP Error: {response.status_code}"


if __name__ == "__main__":
    tools = Tools()
    tools.training_new_iteration(project_name="fruit_object_detection")
