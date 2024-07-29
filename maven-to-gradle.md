# Converting Maven Deploy to Gradle

## Overview
This guide provides instructions on how to convert a Maven-based project to use Gradle for deploying your application. Gradle is a flexible and powerful build automation tool, and migrating from Maven can streamline your build process.

## Prerequisites
* Gradle installed on your system
* Existing Maven project
* Basic understanding of Maven and Gradle

## Steps
* Install Gradle
Ensure Gradle is installed on your system. You can check the installation by running:
```sh
gradle -v
```

* Initialize Gradle in Your Project
Navigate to your project directory and initialize Gradle:
```sh
gradle init
```

* Convert pom.xml Dependencies to build.gradle
Open your pom.xml file and manually copy the dependencies into your new build.gradle file. Below is an example of how to convert dependencies:

> pom.xml
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>2.4.2</version>
    </dependency>
    <!-- Other dependencies -->
</dependencies>
```

>build.gradle:
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web:2.4.2'
    // Other dependencies
}
```

## Configure Deployment in build.gradle
To deploy your project, you need to apply the necessary plugins and configure the repositories and publishing settings.
>Add pluins
```gradle
plugins {
    id 'maven-publish'
}

>Configure Repositories:

```gradle
repositories {
    mavenCentral()
}
'''

## Configure publishing
```gradle
publishing {
    publications {
        mavenJava(MavenPublication) {
            from components.java
            groupId = 'com.example'
            artifactId = 'my-app'
            version = '1.0.0'
        }
    }
    repositories {
        maven {
            name = 'urRepo'
            url = uri('http://my.repo.com/repository/maven-releases/')
            credentials {
                username
```
