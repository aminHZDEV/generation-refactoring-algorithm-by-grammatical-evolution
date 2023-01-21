#!/usr/bin/env python
# coding: utf-8

# In[20]:


import pandas as pd
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from sklearn.mixture import GaussianMixture
import numpy as np
import json


# In[21]:


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


# In[22]:


def draw_ellipse(position, covariance, ax=None, **kwargs):
    """Draw an ellipse with a given position and covariance"""
    ax = ax or plt.gca()

    # Convert covariance to principal axes
    if covariance.shape == (2, 2):
        U, s, Vt = np.linalg.svd(covariance)
        angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
        width, height = 2 * np.sqrt(s)
    else:
        angle = 0
        width, height = 2 * np.sqrt(covariance)

    # Draw the Ellipse
    for nsig in range(1, 4):
        ax.add_patch(Ellipse(position, nsig * width, nsig * height, angle, **kwargs))


# In[23]:


def plot_gmm(gmm, X, label=True, ax=None):
    ax = ax or plt.gca()
    labels = gmm.fit(X).predict(X)
    if label:
        ax.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap="viridis", zorder=2)
    else:
        ax.scatter(X[:, 0], X[:, 1], s=40, zorder=2)
    ax.axis("equal")

    w_factor = 0.2 / gmm.weights_.max()
    for pos, covar, w in zip(gmm.means_, gmm.covars_, gmm.weights_):
        draw_ellipse(pos, covar, alpha=w * w_factor)


# In[24]:


ram = {
    "MM": "MoveMethod",
    "PD": "PushDownMethod",
    "PU": "PullUpMethod",
    "EM": "ExtractMethod",
    "IM": "InlineMethod",
}
rac = {
    "EC": "ExtractClass",
    "MM": "MoveMethod",
    "PU": "PullUpMethod",
    "PD": "PushDownMethod",
}
files = glob("../Resources/refactoring_files/*.csv")
li = []
for filename in files:
    df = pd.read_csv(filename, header=None)
    li.append(df)
data = pd.concat(li, axis=0, ignore_index=True)


# In[25]:


# TODO METHODS
dim = pd.read_csv("../Resources/csv_files/input_cluster/input_method.csv")
for item in data[0]:
    try:
        refactoring_type = item.split("(")[0]
        item = item.split("(")[1].split(",")[0] + "()"
        key = list(ram.keys())[list(ram.values()).index(refactoring_type)]
        if (dim["Method"] == item).any():
            if key == "MM":
                dim.update(
                    pd.DataFrame(
                        {
                            "Method": item,
                            "MM": dim.loc[dim["Method"] == item]["MM"] + 1,
                            "PU": dim.loc[dim["Method"] == item]["PU"],
                            "PD": dim.loc[dim["Method"] == item]["PD"],
                            "EM": dim.loc[dim["Method"] == item]["EM"],
                            "IM": dim.loc[dim["Method"] == item]["IM"],
                        }
                    ),
                    ignore_index=True,
                )
            elif key == "PU":
                dim.update(
                    pd.DataFrame(
                        {
                            "Method": item,
                            "MM": dim.loc[dim["Method"] == item]["MM"],
                            "PU": dim.loc[dim["Method"] == item]["PU"] + 1,
                            "PD": dim.loc[dic["Method"] == item]["PD"],
                            "EM": dim.lom[dic["Method"] == item]["EM"],
                            "IM": dim.loc[dic["Method"] == item]["IM"],
                        }
                    ),
                    ignore_index=True,
                )
            elif key == "PD":
                dim.update(
                    pd.DataFrame(
                        {
                            "Method": item,
                            "MM": dim.loc[dim["Method"] == item]["MM"],
                            "PU": dim.loc[dim["Method"] == item]["PU"],
                            "PD": dim.loc[dim["Method"] == item]["PD"] + 1,
                            "EM": dim.loc[dic["Method"] == item]["EM"],
                            "IM": dim.loc[dim["Method"] == item]["IM"],
                        }
                    ),
                    ignore_index=True,
                )
            elif key == "EM":
                dim.update(
                    pd.DataFrame(
                        {
                            "Method": item,
                            "MM": dim.loc[dim["Method"] == item]["MM"],
                            "PU": dim.loc[dim["Method"] == item]["PU"],
                            "PD": dim.loc[dim["Method"] == item]["PD"],
                            "EM": dim.loc[dim["Method"] == item]["EM"] + 1,
                            "IM": dim.loc[dim["Method"] == item]["IM"],
                        }
                    ),
                    ignore_index=True,
                )
            elif key == "IM":
                dim.update(
                    pd.DataFrame(
                        {
                            "Method": item,
                            "MM": dim.loc[dim["Method"] == item]["MM"],
                            "PU": dim.loc[dim["Method"] == item]["PU"],
                            "PD": dim.loc[dim["Method"] == item]["PD"],
                            "EM": dim.loc[dim["Method"] == item]["EM"],
                            "IM": dim.loc[dim["Method"] == item]["IM"] + 1,
                        }
                    ),
                    ignore_index=True,
                )
        else:
            if key == "MM":
                dim = dim.append(
                    {"Method": item, "MM": 1, "PU": 0, "PD": 0, "EM": 0, "IM": 0},
                    ignore_index=True,
                )
            elif key == "PU":
                dim = dim.append(
                    {"Method": item, "MM": 0, "PU": 1, "PD": 0, "EM": 0, "IM": 0},
                    ignore_index=True,
                )
            elif key == "PD":
                dim = dim.append(
                    {"Method": item, "MM": 0, "PU": 0, "PD": 1, "EM": 0, "IM": 0},
                    ignore_index=True,
                )
            elif key == "EM":
                dim = dim.append(
                    {"Method": item, "MM": 0, "PU": 0, "PD": 0, "EM": 1, "IM": 0},
                    ignore_index=True,
                )
            elif key == "IM":
                dim = dim.append(
                    {"Method": item, "MM": 0, "PU": 0, "PD": 0, "EM": 0, "IM": 1},
                    ignore_index=True,
                )
    except:
        continue

dim.to_csv(
    "../Resources/csv_files/input_cluster/input_method.csv",
    encoding="utf-8",
    index=False,
)
dim


# In[26]:


dic = pd.read_csv("../Resources/csv_files/input_cluster/input_class.csv")
for item in data[0]:
    try:
        refactoring_type = item.split("(")[0]
        key = list(rac.keys())[list(rac.values()).index(refactoring_type)]

        if key == "EC":
            item = item.split("(")[1].split(",")[0]
        else:
            item = item.split("(")[1].split(",")[0]
            temp = item.split(".")
            item = item.replace("." + temp[len(temp) - 1], "")
        item = item.replace(")", "")

        if (dic["Class"] == item).any():
            if key == "EC":
                dic.update(
                    pd.DataFrame(
                        {
                            "Class": item,
                            "EC": dic.loc[dic["Class"] == item]["EC"] + 1,
                            "MM": dic.loc[dic["Class"] == item]["MM"],
                            "PU": dic.loc[dic["Class"] == item]["PU"],
                            "PD": dic.loc[dic["Class"] == item]["PD"],
                        }
                    )
                )
            elif key == "MM":
                dic.update(
                    pd.DataFrame(
                        {
                            "Class": item,
                            "EC": dic.loc[dic["Class"] == item]["EC"],
                            "MM": dic.loc[dic["Class"] == item]["MM"] + 1,
                            "PU": dic.loc[dic["Class"] == item]["PU"],
                            "PD": dic.loc[dic["Class"] == item]["PD"],
                        }
                    )
                )
            elif key == "PU":
                dic.update(
                    pd.DataFrame(
                        {
                            "Class": item,
                            "EC": dic.loc[dic["Class"] == item]["EC"],
                            "MM": dic.loc[dic["Class"] == item]["MM"],
                            "PU": dic.loc[dic["Class"] == item]["PU"] + 1,
                            "PD": dic.loc[dic["Class"] == item]["PD"],
                        }
                    )
                )
            elif key == "PD":
                dic.update(
                    pd.DataFrame(
                        {
                            "Class": item,
                            "EC": dic.loc[dic["Class"] == item]["EC"],
                            "MM": dic.loc[dic["Class"] == item]["MM"],
                            "PU": dic.loc[dic["Class"] == item]["PU"],
                            "PD": dic.loc[dic["Class"] == item]["PD"] + 1,
                        }
                    )
                )
        else:

            if key == "EC":
                dic = dic.append(
                    {"Class": item, "EC": 1, "MM": 0, "PU": 0, "PD": 0},
                    ignore_index=True,
                )
            elif key == "MM":
                dic = dic.append(
                    {"Class": item, "EC": 0, "MM": 1, "PU": 0, "PD": 0},
                    ignore_index=True,
                )
            elif key == "PU":
                dic = dic.append(
                    {"Class": item, "EC": 0, "MM": 0, "PU": 1, "PD": 0},
                    ignore_index=True,
                )
            elif key == "PD":
                dic = dic.append(
                    {"Class": item, "EC": 0, "MM": 0, "PU": 0, "PD": 1},
                    ignore_index=True,
                )
    except Exception as e:
        #         print("ERROR : ", e)
        continue
dic.to_csv(
    "../Resources/csv_files/input_cluster/input_class.csv",
    encoding="utf-8",
    index=False,
)
dic


# In[27]:


X = dic.iloc[:, 1:5]
Y = dim.iloc[:, 1:6]
d = pd.DataFrame(X)
c = pd.DataFrame(Y)

model = GaussianMixture(
    n_components=2,
    covariance_type="full",
    max_iter=100,
    n_init=1,
    init_params="kmeans",
    verbose=0,
    random_state=1,
)

# Fit the model and predict labels
clust = model.fit(d)
labels = model.predict(d)
my_class_dict = {}
for i, item in enumerate(np.unique(labels)):
    a = dic[labels == item]
    my_class_dict.update(
        {
            i: [
                {"EC": {"MAX": int(a.EC.max()), "MIN": int(a.EC.min())}},
                {"MM": {"MAX": int(a.MM.max()), "MIN": int(a.MM.min())}},
                {"PU": {"MAX": int(a.PU.max()), "MIN": int(a.PU.min())}},
                {"PD": {"MAX": int(a.PU.max()), "MIN": int(a.PD.min())}},
            ]
        }
    )

#     my_class_dict = {i:{}}

model = GaussianMixture(
    n_components=6,
    covariance_type="full",
    max_iter=100,
    n_init=1,
    init_params="kmeans",
    verbose=0,
    random_state=1,
)

# Fit the model and predict labels
clust = model.fit(c)
labels1 = model.predict(c)
my_method_dict = {}
for i, item in enumerate(np.unique(labels1)):
    a = dim[labels1 == item]
    my_method_dict.update(
        {
            i: [
                {"MM": {"MAX": int(a.MM.max()), "MIN": int(a.MM.min())}},
                {"PU": {"MAX": int(a.PU.max()), "MIN": int(a.PU.min())}},
                {"PD": {"MAX": int(a.PU.max()), "MIN": int(a.PD.min())}},
                {"EM": {"MAX": int(a.EM.max()), "MIN": int(a.EM.min())}},
                {"IM": {"MAX": int(a.IM.max()), "MIN": int(a.IM.min())}},
            ]
        }
    )


with open("../Resources/json_files/class_cluster.json", "w") as fp:
    json.dump(my_class_dict, fp)

with open("../Resources/json_files/method_cluster.json", "w") as fp:
    json.dump(my_method_dict, fp)

