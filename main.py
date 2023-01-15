from Dependencies.DatasetsProvider import DataSetsProvider
from Dependencies.ClsUDBMetrics import ClsUDB_Metrics
from Dependencies.GenBase import GenBase

ds_instance = DataSetsProvider()
cu_instance = ClsUDB_Metrics()

# clone projects
# try:
#     ds_instance.get_datasets()
# except Exception as e:
#     print("ERROR : ", e)


# create .und db and refactoring .json file
# for item in ds_instance.get_resource_path():
#     cu_instance.create_understand_database_from_project(root_path=item)
#     ds_instance.refactoringminer(git_repo_folder=item)


# METHOD METRICS

# for item in ds_instance.get_resource_path():
#     cu_instance.get_metrics_of_each_function(my_path=item)

# CLASS METRICS

# for item in ds_instance.get_resource_path():
#     cu_instance.get_metrics_of_each_class(my_path=item)

# DEP CLASSES

# for item in ds_instance.get_resource_path():
#     cu_instance.get_dep_of_each_class(db_path=item, csv_path="Resources/csv_files/")

# GENBASE
a = GenBase()
a.run()
