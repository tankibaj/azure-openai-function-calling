from functions.argocd_controller import ArgoCDController


def get_available_applications() -> dict:
    """Retrieve the names of all ArgoCD applications available on the Kubernetes cluster.

    Use this function when you want to get a list of all ArgoCD applications currently deployed on the cluster.

    :return: A dictionary containing a list of application names or any error message.
    """
    controller = ArgoCDController()
    return controller.get_all_applications()


def deploy_application(manifest_path: str) -> dict:
    """Deploy an ArgoCD application on the Kubernetes cluster using a manifest file.

    Use this function when you want to deploy or update an ArgoCD application on the cluster.
    The function will decide whether to create a new application or update an existing one based on the manifest.

    :param manifest_path: The file path to the ArgoCD application manifest (YAML format).
    :return: A dictionary indicating the deployment status or any error message.
    """
    controller = ArgoCDController()
    return controller.deploy_argocd_application(manifest_path)


def get_application_status(app_name: str) -> dict:
    """Retrieve the health and sync status of a specific ArgoCD application.

    Use this function when you want to check the current status of an ArgoCD application on the cluster.
    It provides information about the application's health and synchronization status.

    :param app_name: The name of the ArgoCD application.
    :return: A dictionary containing the health status, sync status, and any error message (if applicable).
    """
    controller = ArgoCDController()
    return controller.get_argocd_application_status(app_name)


def delete_application(app_name: str) -> dict:
    """Delete an ArgoCD application from the Kubernetes cluster.

    Use this function when you want to remove a specific ArgoCD application from the cluster.
    The function will attempt to delete the application and return the status of the operation.

    :param app_name: The name of the ArgoCD application to delete.
    :return: A dictionary indicating the deletion status or any error message.
    """
    controller = ArgoCDController()
    return controller.delete_argocd_application(app_name)


if __name__ == "__main__":
    # -- Check if the user is authenticated
    # controller = ArgoCDController()
    # print(controller.check_authentication())

    # -- Retrieve the names of all ArgoCD applications
    apps = get_available_applications()
    print(apps)

    # -- Deploy the ArgoCD application using the manifest file
    # manifest_path = "manifests/guestbook.yaml"
    # deploy_result = deploy_application(manifest_path)
    # print(deploy_result)

    # -- Retrieve the ArgoCD application's status
    # app_name = "guestbook"
    # status_result = get_application_status(app_name)
    # print(status_result)

    # -- Delete the ArgoCD application
    # app_name = "guestbook"
    # delete_result = delete_application(app_name)
    # print(delete_result)
