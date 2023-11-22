import requests
import yaml
import logging
import config

logger = logging.getLogger(__name__)


class ArgoCDController:
    argocd_url = config.argocd_url
    argocd_api_key = config.argocd_api_key

    if argocd_api_key is None:
        raise ValueError("ARGOCD_API_KEY is not defined")
    ARGOCD_API_URL = f"{argocd_url}/api/v1/applications"
    HEADERS = {
        "Authorization": f"Bearer {argocd_api_key}",
        "Content-Type": "application/json"
    }

    def __init__(self):
        pass

    def check_authentication(self) -> dict:
        """
        Check if the provided authentication token is valid for ArgoCD.

        :return: A dictionary indicating the authentication status or any error message.
        """
        try:
            response = requests.get(self.ARGOCD_API_URL, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            logger.info("Authentication check successful.")
            return {"authenticated": True}
        except requests.HTTPError as e:
            if e.response.status_code == 401:  # Unauthorized
                logger.warning("Invalid authentication token.")
                return {"authenticated": False, "error": "Invalid authentication token."}
            logger.error(f"Authentication check failed: {e}")
            return {"authenticated": False, "error": f"Authentication check failed: {e}"}

    def get_all_applications(self) -> dict:
        """
        Retrieve the names of all ArgoCD applications available on the cluster.

        :return: A dictionary containing a list of application names or any error message.
        """
        try:
            response = requests.get(self.ARGOCD_API_URL, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()
            applications = data["items"]
            application_names = [application['metadata']['name'] for application in applications]
            return {"applications": application_names}
        except requests.HTTPError as e:
            logger.error(f"Error retrieving available applications: {e}")
            return {"error": f"Error retrieving available applications: {e}"}

    def application_exists(self, app_name: str) -> dict:
        """Determine if an ArgoCD application exists on the cluster."""
        try:
            response = requests.get(f"{self.ARGOCD_API_URL}/{app_name}", headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            return {"exists": True}
        except requests.HTTPError as e:
            if e.response.status_code in [403, 404]:  # Forbidden or Not Found
                return {"exists": False}
            logger.error(f"Error checking application existence for '{app_name}': {e}")
            return {"error": f"Error checking application existence: {e}"}

    def update_argocd_application(self, app_name: str, manifest: dict) -> dict:
        """Update an existing ArgoCD application on the cluster."""
        try:
            response = requests.put(f"{self.ARGOCD_API_URL}/{app_name}", headers=self.HEADERS, json=manifest,
                                    timeout=10)
            response.raise_for_status()
            logger.info(f"Application '{app_name}' updated successfully.")
            return {"status": "updated"}
        except requests.HTTPError as e:
            logger.error(f"Failed to update application '{app_name}': {e}")
            return {"error": f"Failed to update application '{app_name}': {e}"}

    def create_new_argocd_application(self, manifest: dict) -> dict:
        """Create a new ArgoCD application on the cluster."""
        try:
            response = requests.post(self.ARGOCD_API_URL, headers=self.HEADERS, json=manifest, timeout=10)
            response.raise_for_status()
            app_name = manifest['metadata']['name']
            logger.info(f"Application '{app_name}' created successfully.")
            return {"status": "created"}
        except requests.HTTPError as e:
            logger.error(f"Failed to deploy application: {e}")
            return {"error": f"Failed to deploy application: {e}"}

    def deploy_argocd_application(self, manifest_path: str) -> dict:
        """Deploy an ArgoCD application/manifest on the Kubernetes cluster."""
        with open(manifest_path, 'r') as file:
            manifest = yaml.safe_load(file)

        app_name = manifest['metadata']['name']

        if self.application_exists(app_name).get("exists"):
            logger.info(f"Application '{app_name}' exists. Updating...")
            return self.update_argocd_application(app_name, manifest)
        else:
            logger.info(f"Application '{app_name}' does not exist. Creating...")
            return self.create_new_argocd_application(manifest)

    def get_argocd_application_status(self, app_name: str) -> dict:
        """Retrieve the health and sync status of a specific ArgoCD application."""
        try:
            response = requests.get(f"{self.ARGOCD_API_URL}/{app_name}", headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            app_data = response.json()

            health_status = app_data['status']['health']['status']
            sync_status = app_data['status']['sync']['status']

            return {
                "health_status": health_status,
                "sync_status": sync_status,
                "error": None
            }
        except requests.HTTPError as e:
            logger.error(f"Failed to fetch application status for '{app_name}': {e}")
            return {
                "health_status": None,
                "sync_status": None,
                "error": f"Failed to fetch application status: {e}"
            }

    def delete_argocd_application(self, app_name: str) -> dict:
        """
        Delete a specific ArgoCD application from the cluster.

        :param app_name: The name of the ArgoCD application to delete.
        :return: A dictionary indicating the deletion status or any error message.
        """
        try:
            response = requests.delete(f"{self.ARGOCD_API_URL}/{app_name}", headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            logger.info(f"Application '{app_name}' deleted successfully.")
            return {"status": "deleted"}
        except requests.HTTPError as e:
            logger.error(f"Failed to delete application '{app_name}': {e}")
            return {"error": f"Failed to delete application '{app_name}': {e}"}
