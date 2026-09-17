// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE at repository root.
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "FreshCheck"
include(":app")
