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
    agent none
    triggers {
        cron('@daily')
    }
    options {
        disableConcurrentBuilds()  //each branch has 1 job running at a time

    }

     parameters {
        booleanParam(name: "FRESH_WORKSPACE", defaultValue: false, description: "Purge workspace before staring and checking out source")
        string(name: "PROJECT_NAME", defaultValue: "Medusa Downloader", description: "Name given to the project")
    }
    stages{
        stage("Getting Distribution Info"){
            agent {
              dockerfile {
                    filename 'ci\\docker\\windows\\Dockerfile'
                    label 'windows&&docker'
                  }
            }
            steps{
               timeout(5) {
                   bat "python setup.py dist_info"
               }
            }
            post{
                success{
                    stash includes: "medusaDownloader.dist-info/**", name: 'DIST-INFO'
                    archiveArtifacts artifacts: "medusaDownloader.dist-info/**"
                }
                cleanup{
                    cleanWs(deleteDirs: true,
                            notFailBuild: true
                        )
                }
            }
        }
        stage("Build"){
            agent{
                dockerfile {
                    filename 'ci\\docker\\windows\\Dockerfile'
                    label 'windows&&docker'
                  }
            }
            options{
                timeout(5)
            }
            stages{

                stage("Building Python Package"){
                    steps {
                        bat "if not exist logs mkdir logs"
                        powershell "& python setup.py build -b build  | tee logs\\build.log"

                    }
                    post{
                        always{
                            archiveArtifacts artifacts: "logs/build.log"
                        }
                        failure{
                            echo "Failed to build Python package"
                        }
                    }
                }
            }
            post{
                cleanup{
                    cleanWs(deleteDirs: true,
                            notFailBuild: true
                        )
                }
            }
        }
        stage("Tests") {
            agent{
                dockerfile {
                    filename 'ci\\docker\\windows\\Dockerfile'
                    label 'windows&&docker'
                  }
            }
            options{
                timeout(5)
            }
            stages{
                stage("Setting up tests"){
                    steps{
                        bat "if not exist logs mkdir logs"
                        bat "if not exist reports mkdir reports"
                    }
                }
                stage("Run tests"){
                    parallel {
                        stage("PyTest"){
                            steps{
                                bat "pytest.exe --junitxml=${WORKSPACE}/reports/junit-${env.NODE_NAME}-pytest.xml --junit-prefix=${env.NODE_NAME}-pytest --cov-report html:${WORKSPACE}/reports/coverage/ --cov=medusadownloader" //  --basetemp={envtmpdir}"

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
                                bat "mypy.exe -p medusadownloader --html-report ${WORKSPACE}/reports/mypy_html > logs\\mypy.log"
                            }
                            post{
                                always {
                                    recordIssues(tools: [myPy(pattern: "logs/mypy.log")])
                                    publishHTML([allowMissing: true, alwaysLinkToLastBuild: false, keepAll: false, reportDir: 'reports/mypy_html', reportFiles: 'index.html', reportName: 'MyPy', reportTitles: ''])
                                }
                            }
                        }
                        stage("Run Flake8 Static Analysis") {
                            steps{
                                script{
                                    try{
                                        bat "flake8 medusadownloader --tee --output-file=${WORKSPACE}\\logs\\flake8.log"
                                    } catch (exc) {
                                        echo "flake8 found some warnings"
                                    }
                                }
                            }
                            post {
                                always {
                                    recordIssues(tools: [flake8(pattern: 'logs/flake8.log')])
                                }
                                cleanup{
                                    cleanWs(patterns: [[pattern: 'logs/flake8.log', type: 'INCLUDE']])
                                }
                            }
                        }
                    }
                    post{
                        cleanup{
                            cleanWs(deleteDirs: true,
                                    notFailBuild: true
                                )
                        }
                    }
                }
            }
        }
        stage("Packaging") {
            agent{
                dockerfile {
                    filename 'ci\\docker\\windows\\Dockerfile'
                    label 'windows&&docker'
                  }
            }
            options{
                timeout(5)
            }
            steps{
                bat script: "python.exe setup.py sdist -d ${WORKSPACE}\\dist bdist_wheel -d ${WORKSPACE}\\dist"
            }

            post {
                success {
                    archiveArtifacts artifacts: "dist/*.whl,dist/*.tar.gz,dist/*.zip", fingerprint: true
                }
                cleanup{
                    cleanWs(deleteDirs: true,
                            
                            notFailBuild: true
                        )
                }
            }
        }
    }
}
