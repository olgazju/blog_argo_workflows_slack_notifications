# blog_argo_workflows_slack_notifications


### Development Setup

Follow these steps to set up your development environment:

1. **Clone the repository**:

```bash
git clone https://github.com/olgazju/blog_argo_workflows_slack_notifications.git
cd blog_argo_workflows_slack_notifications
```

2. **Create and activate a virtual environment**:

```bash
brew update && brew install pyenv pyenv-virtualenv
pyenv install 3.12.2
pyenv virtualenv 3.12.2 blog_argo_workflows_slack_notifications
pyenv local blog_argo_workflows_slack_notifications
```

3.  **Install the required dependencies**:

```bash
pip install -r requirements.txt
```

4. **Install and configure pre-commit hooks**:

```bash
pip install pre-commit
pre-commit install
```

5. **Run pre-commit hooks manually (optional)**:

```bash
pre-commit run --all-files
```
