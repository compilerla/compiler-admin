# Getting Started

This tutorial will guide you through the initial setup of the `compiler-admin` tool, including cloning the repository and initializing the necessary configurations for Google Workspace access.

## 1. Clone the Repository

First, clone the `compiler-admin` repository to your local machine and create the configuration directory it uses.

```bash
mkdir -p ~/.config/compiler-admin
git clone https://github.com/compilerla/compiler-admin.git
cd compiler-admin
```

## 2. Open in Development Container

This project is configured to use a VS Code Development Container. Open the cloned repository in VS Code. You should be prompted to "Reopen in Container". Click that button to build and open the development environment.

This ensures you have all the required dependencies, like GAM7 and GYB, installed and ready to go.

## 3. Initialize the Project

Before you can use `compiler-admin` to manage Google Workspace, you need to authorize it to use the necessary Google APIs. This is done using the `init` command.

This command will set up a Google Cloud Platform (GCP) project with the required APIs enabled and create the necessary OAuth credentials for both GAM (for user/group management) and GYB (for Gmail backups).

To run the initialization, you need to provide your Compiler Google account username (the part before `@compiler.la`).

```bash
compiler-admin init --gam --gyb your_username
```

Follow the prompts from GAM and GYB. You will be asked to go through a web-based OAuth flow to grant permissions.

For more detailed information on the underlying tools, you can refer to their documentation:

- [GAM7 Wiki](https://github.com/GAM-team/GAM/wiki/#requirements)
- [GYB Wiki](https://github.com/GAM-team/got-your-back/wiki)

Once this is complete, your `compiler-admin` tool is ready to use.
