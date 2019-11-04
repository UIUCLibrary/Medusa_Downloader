@Library(["devpi", "PythonHelpers"]) _
def remove_from_devpi(devpiExecutable, pkgName, pkgVersion, devpiIndex, devpiUsername, devpiPassword){
    script {
            try {
                bat "${devpiExecutable} login ${devpiUsername} --password ${devpiPassword}"
                bat "${devpiExecutable} use ${devpiIndex}"
                bat "${devpiExecutable} remove -y ${pkgName}==${pkgVersion}"
            } catch (Exception ex) {
                echo "Failed to remove ${pkgName}==${pkgVersion} from ${devpiIndex}"
        }

    }
}


def get_package_version(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Version
        }
    }
}

def get_package_name(stashName, metadataFile){
    ws {
        unstash "${stashName}"
        script{
            def props = readProperties interpolate: true, file: "${metadataFile}"
            deleteDir()
            return props.Name
        }
    }
}




pipeline {
    agent {
        label "Windows"
    }
    triggers {
        cron('@daily')
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time
        timeout(60)  // Timeout after 60 minutes. This shouldn't take this long but it hangs for some reason
        checkoutToSubdirectory("source")
    }
    environment {
        PATH = "${tool 'CPython-3.6'};${tool 'CPython-3.7'};$PATH"
        //DEVPI = credentials("DS_devpi")
    }

     parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        string(name: "PROJECT_NAME", defaultValue: "Medusa Downloader", description: "Name given to the project")
    }
    stages{
        stage("Configure") {
            environment{
                PATH = "${tool 'CPython-3.6'};$PATH"
            }
            stages{
                stage("Purge all existing data in workspace"){
                    when{
                        equals expected: true, actual: params.FRESH_WORKSPACE
                    }
                    steps {
                        deleteDir()
                        bat "dir"
                        echo "Cloning source"
                        dir("source"){
                            checkout scm
                        }
                    }
                    post{
                        success {
                            bat "dir /s /B"
                        }
                    }
                }
                stage("Getting Distribution Info"){
                    environment{
                        PATH = "${tool 'CPython-3.7'};$PATH"
                    }
                    steps{
                        dir("source"){
                            bat "python setup.py dist_info"
                        }
                    }
                    post{
                        success{
                            dir("source"){
                                stash includes: "medusaDownloader.dist-info/**", name: 'DIST-INFO'
                                archiveArtifacts artifacts: "medusaDownloader.dist-info/**"
                            }
                        }
                    }
                }
                stage("Creating virtualenv for building"){
                    steps{
                        bat "python -m venv venv"
                        script {
                            try {
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip"
                            }
                            catch (exc) {
                                bat "python -m venv venv"
                                bat "call venv\\Scripts\\python.exe -m pip install -U pip --no-cache-dir"
                            }
                        }
                        bat "venv\\Scripts\\pip.exe install -U setuptools"
                        bat "venv\\Scripts\\pip.exe install tox pytest pytest-cov lxml mypy flake8 sphinx wheel --upgrade-strategy only-if-needed"
//                        bat "venv\\Scripts\\pip.exe install detox==0.13 tox==3.2.1 mypy pytest pytest-cov flake8 sphinx wheel"
                    }
                    post{
                        success{
                            bat "(if not exist logs mkdir logs) && venv\\Scripts\\pip.exe list > ${WORKSPACE}\\logs\\pippackages_venv_${NODE_NAME}.log"
                            archiveArtifacts artifacts: "logs/pippackages_venv_${NODE_NAME}.log"
                        }
                    }
                }
            }
        }
        stage("Build"){
            stages{
                stage("Building Python Package"){
                    steps {


                        dir("source"){
                            powershell "& ${WORKSPACE}\\venv\\Scripts\\python.exe setup.py build -b ${WORKSPACE}\\build  | tee ${WORKSPACE}\\logs\\build.log"
                        }

                    }
                    post{
                        always{
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'Pep8', pattern: 'logs/build.log']]
                            archiveArtifacts artifacts: "logs/build.log"
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                    }
                }
            }
        }
        stage("Tests") {

            parallel {
                stage("PyTest"){
                    steps{
                        dir("source"){
                            bat "${WORKSPACE}\\venv\\Scripts\\pytest.exe --junitxml=${WORKSPACE}/reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/ --cov=medusadownloader" //  --basetemp={envtmpdir}"
                        }

                    }
                    post {
                        always{
                            junit "reports/junit-${env.NODE_NAME}-pytest.xml"
                            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/coverage', reportFiles: 'index.html', reportName: 'Coverage', reportTitles: ''])
                        }
                    }
                }
                stage("MyPy"){
                    steps{
                        dir("source") {
                            bat "${WORKSPACE}\\venv\\Scripts\\mypy.exe -p medusadownloader --junit-xml=${WORKSPACE}/junit-${env.NODE_NAME}-mypy.xml --html-report ${WORKSPACE}/reports/mypy_html"
                        }
                    }
                    post{
                        always {
                            junit "junit-${env.NODE_NAME}-mypy.xml"
                            publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                        }
                    }
                }
                stage("Run Flake8 Static Analysis") {
                    steps{
                        script{
                            try{
                                dir("source"){
                                    bat "${WORKSPACE}\\venv\\Scripts\\flake8.exe hsw --format=medusadownloader --tee --output-file=${WORKSPACE}\\logs\\flake8.log"
                                }
                            } catch (exc) {
                                echo "flake8 found some warnings"
                            }
                        }
                    }
                    post {
                        always {
                            warnings canRunOnFailed: true, parserConfigurations: [[parserName: 'PyLint', pattern: 'logs/flake8.log']], unHealthy: ''
                        }
                        cleanup{
                            cleanWs(patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']])
                        }
                    }
                }

            }
        }
        stage("Packaging") {
            parallel {
                stage("Source and Wheel formats"){
                    when {
                        equals expected: true, actual: params.PACKAGE_PYTHON_FORMATS
                    }

                    steps{
                        dir("source"){
                            bat script: "venv\\Scripts\\python.exe setup.py sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
                        }
                    }

                    post {
                        success {
                            dir("dist") {
                                archiveArtifacts artifacts: "*.whl", fingerprint: true
                                archiveArtifacts artifacts: "*.tar.gz", fingerprint: true
                                archiveArtifacts artifacts: "*.zip", fingerprint: true
                            }
                        }
                        failure {
                            echo "Failed to package."
                        }
                    }
                }
            }
        }
    }
    post {
        cleanup{
            cleanWs(
                deleteDirs: true,
                patterns: [
                    [pattern: 'source', type: 'INCLUDE'],
                    [pattern: 'build*', type: 'INCLUDE'],
                    [pattern: 'certs', type: 'INCLUDE'],
                    [pattern: 'dist*', type: 'INCLUDE'],
                    [pattern: 'logs*', type: 'INCLUDE'],
                    [pattern: 'reports*', type: 'INCLUDE'],
//                    [pattern: '.tox', type: 'INCLUDE'],
                    [pattern: '*@tmp', type: 'INCLUDE']
                    ]
                )
        }
    }
}
//pipeline {
//  agent any
//  stages {
//    stage("Cloning Source") {
//            agent any
//
//            steps {
//                deleteDir()
//                echo "Cloning source"
//                checkout scm
//                stash includes: '**', name: "Source", useDefaultExcludes: false
//
//            }
//
//        }
//
//    stage('Unit Tests') {
//      steps {
//        node(label: 'Windows') {
//          deleteDir()
//          unstash "Source"
//          bat "${env.PYTHON3} setup.py testxml"
//          junit 'reports/junit*.xml'
//        }
//
//      }
//    }
//    stage("Packaging") {
//      steps{
//        parallel(
//          "Source Release": {
//            deleteDir()
//            unstash "Source"
//            sh "${env.PYTHON3} setup.py sdist"
//            archiveArtifacts artifacts: "dist/**", fingerprint: true
//          },
//
//          "MSI Release": {
//            node(label: "Windows") {
//              deleteDir()
//              unstash "Source"
//              bat "${env.PYTHON3} setup-freeze.py bdist_msi --add-to-path=true"
//              archiveArtifacts artifacts: "dist/**", fingerprint: true
//            }
//          },
//        )
//      }
//    }
//  }
//}
