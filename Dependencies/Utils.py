import subprocess
import os


def git_restore(project_dir):
    """
    This function returns a git supported project back to the initial commit

    Args:

        project_dir (str): The absolute path of project's directory.

    Returns:

        None

    """
    assert os.path.isdir(project_dir)
    print("TEST PATH : ", os.path.join(project_dir, ".git"))
    assert os.path.isdir(os.path.join(project_dir, ".git"))
    subprocess.Popen(
        ["git", "restore", "."], cwd=project_dir, stdout=open(os.devnull, "wb")
    ).wait()
    subprocess.Popen(
        ["git", "clean", "-f", "-d"], cwd=project_dir, stdout=open(os.devnull, "wb")
    ).wait()
