# Contributing
This project is maintained by Rahul Singh of [Anant](http://anant.us). Feel free contact me if you'd like to collaborate on this and other tools. I also work on [Cassandra.Link](http://cassandra.link), a curated set of knowledge on all things related to Cassandra.

### Table of Contents
- [Setting up a Development Environment](#setting-up-a-development-environment)
- [Contribution Guidelines](#contribution-guidelines)


## Setting up a Development Environment
To quickly get started developing on this project, we recommend using [CCM, the Cassandra Cluster Manager](https://github.com/riptano/ccm). We describe how to setup a test cluster using CCM [here](./setup/README.md#sandbox-clusters-for-testing-and-development).

You can also test out individual tools quickly using docker, without having to setup everything in Ansible. We provide some sample scripts to make it easy. [Click here for instructions](../src/docker/README.md).

## Contribution Guidelines
In order to keep this project organized, please keep in mind the following principles when adding or modifying tools and documentation to cassandra.toolkit. 

#### Directory Structure

| Directory | Purpose | 
| ------------------- | ------------------ |
| [`config/`](../config) | All configs (e.g., yamls, .ini files, etc) that users interact with should go here. They might choose to look at other config files in for example the `src/` dir, but they should not have to if they follow the instructions. Consider every other dir except for this one READ-ONLY for the end-user. |
| [`docs/`](../docs) | All documentation files should go here, including  |
| [`docs/cluster-maintenance/`](../docs/cluster-maintenance) | All documentation required to use the tools in cassandra.toolkit tools goes here. Documentation related to setting up the tools should not go here; it should go in `docs/setup/`. The main README.md in this dir functions as an index for all the other documentation files in this dir. |
| [`docs/setup/`](../docs/setup) | All documentation required to setup a new Cassandra cluster and to install and start cassandra.toolkit tools goes here. Documentation related to actually using the tools should not go here; it should go in `docs/cluster-maintenance/`. The main README.md in this dir functions as an index for all the other documentation files in this dir. |
| [`docs/assets/`](../docs/assets) | All image files and other documentation related assets for the project should go here |
| [`quickstart-tutorials/`](../quickstart-tutorials) | These are kind of unrelated to cassandra.toolkit, but provide easy to use starter files to setup Cassandra related tooling on localhost. Nothing should go in here that is actually required for cassandra.toolkit to work. |
| [`src/`](../src/) | This is the low-level source code for the project, including ansible files and docker related files that are used in cassandra.toolkit. Documentation in this directory and all subdirectories should be mostly for developers, not for end-users, though of course some end-users will want to look in here to see what is going on under the hood. |

#### How to: Add Documentation

Our goal is to make it easy for new users should be able to open cassandra.toolkit in Github or in their IDE and easily know exactly how to navigate through the project from start to finish. 

Accordingly, the project root README.md should be simple and easy to navigate. Don't add to much here, just enough so that users can find what they need here and then be redirected to the documentation that they are looking for. 

- **Links** should be relative paths when internal to the project (as modelled within this file). This makes it so users in IDEs or Github can click on them and follow them easily. Add links liberally so that it is easy to navigate through the documentation, though not too many in order to avoid making the documentation too cluttered.
- Larger documentation files should have a **Table of Contents** at the top, that is labelled as such.

#### How to: Add Tools

- All directories and subdirectories should have their own `README.md` file describing the purpose of the directory, so as to keep the project organized. Before adding files to cassandra.toolkit, check the directory you are about to add it to and make sure this is where it belongs.