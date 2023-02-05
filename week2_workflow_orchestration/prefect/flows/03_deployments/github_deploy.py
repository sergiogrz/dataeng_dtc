from prefect.deployments import Deployment
from parameterized_flow import etl_parent_flow
from prefect.filesystems import GitHub

github_block = GitHub.load("dataeng-dtc-gh")

github_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name="github-flow",
    storage=github_block,
    entrypoint="parameterized_flow.py:etl_parent_flow",
)

if __name__ == "__main__":
    github_dep.apply()
