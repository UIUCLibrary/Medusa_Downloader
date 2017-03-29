pipeline {
  agent any
  stages {
    stage('Unit Tests') {
      steps {
        node(label: 'Windows') {
          checkout scm
          bat "${env.PYTHON3} setup.py testxml"
          junit 'reports/junit*.xml'
        }

      }
    }
    stage("Packaging") {
      steps{
        parallel(
          "Source Release": {
            deleteDir()
            checkout scm
            sh "${env.PYTHON3} setup.py sdist"
            archiveArtifacts artifacts: "dist/**", fingerprint: true
          },
          "MSI Release": {
            deleteDir()
            checkout scm
            bat "${env.PYTHON3} setup.py bdist_msi"
            archiveArtifacts artifacts: "dist/**", fingerprint: true
          }
        )
      }
    }
  }
}
