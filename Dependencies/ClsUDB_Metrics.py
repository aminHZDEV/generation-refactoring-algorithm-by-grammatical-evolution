import os
import subprocess
import understand
from dotenv import dotenv_values


class ClsUDB_Metrics:
    def __init__(self):
        pass

    def create_understand_database_from_project(self, root_path):
        """
        This function creates understand database for the given project directory.
        Args:
            project_dir (str): The absolute path of project's directory.
            db_dir (str): The absolute directory path to save Understand database (.udb or .und binary file)
        Returns:
            str: Understand database path
        """
        my_path = os.getcwd() + "/Resources/" + root_path
        assert os.path.isdir(my_path)
        db_name = os.path.basename(os.path.normpath(root_path)) + ".und"
        db_path = os.path.join("Resources/und_db/", db_name)
        if os.path.exists(db_path):
            return db_path
        # An example of command-line is:
        # und create -languages c++ add @myFiles.txt analyze -all myDb.udb
        # understand_5_cmd = ['und', 'create', '-languages', 'Java', 'add', project_dir, 'analyze', '-all', db_path]
        understand_6_cmd = ["und", "create", "-db", db_path, "-languages", "java"]
        understand_7_cmd = [
            "und",
            "-db",
            db_path,
            "add",
            "Resources/" + root_path,
            "analyze",
            "-all",
        ]

        result = subprocess.run(
            understand_6_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result_2 = subprocess.run(
            understand_7_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            error_ = result.stderr.decode("utf-8")
            print(f"return code: {result.returncode} msg: {error_}")
        else:
            print(f"Understand project was created successfully!")

        if result_2.returncode != 0:
            error_ = result_2.stderr.decode("utf-8")
            print(f"return code: {result_2.returncode} msg: {error_}")
        else:
            print(f"Understand analyze successfully!")

        return db_path

    def get_metrics(self, my_path):
        db = understand.open("Resources/und_db/" + my_path + ".und")
        metrics = db.metric(dotenv_values().get("LIST_METRICS_CLASS").split(" "))
        for k, v in sorted(metrics.items()):
            print(k, "=", v)

    def get_metrics_of_each_function(self, my_path: str):
        db = understand.open("Resources/und_db/" + my_path + ".und")
        for func in db.ents("function,method,procedure"):
            metric = func.metric(dotenv_values().get("LIST_METRICS_METHOD").split(" "))
            for k, v in metric.items():
                print(k, "=", v)

    def get_metrics_of_each_class(self, my_path: str):
        db = understand.open("Resources/und_db/" + my_path + ".und")
        for func in db.ents("class"):
            metric = func.metric(dotenv_values().get("LIST_METRICS_CLASS").split(" "))
            for k, v in metric.items():
                print(k, "=", v)

    def get_dep_of_each_class(self, csv_path: str, db_path: str):
        """
        Exports understand dependencies into a csv file.
        :param csv_path: The absolute address of csv file to generate.
        :param db_path: The absolute address of project path.
        :return: None
        """

        csv_path = csv_path + db_path + "_dep.csv"
        db_path = "Resources/und_db/" + db_path + ".und"
        command = [
            "und",
            "export",
            "-db",
            db_path,
            "-dependencies",
            "class",
            "matrix",
            csv_path,
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            error_ = result.stderr.decode("utf-8")
            print(f"return code: {result.returncode} msg: {error_}")
        else:
            print("Modular dependency graph (MDG.csv) was exported.")
