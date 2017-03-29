pipeline {
  agent any
  stages {
    stage("Cloning Source") {
            agent any

            steps {
                deleteDir()
                echo "Cloning source"
                checkout scm
                stash includes: '**', name: "Source", useDefaultExcludes: false

            }

        }

    stage('Unit Tests') {
      steps {
        node(label: 'Windows') {
          deleteDir()
          unstash "Source"
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
            unstash "Source"
            sh "${env.PYTHON3} setup.py sdist"
            archiveArtifacts artifacts: "dist/**", fingerprint: true
          },
          
          "MSI Release": {
            node(label: "Windows") {
              deleteDir()
              unstash "Source"
              bat "${env.PYTHON3} setup.py bdist_msi"
              archiveArtifacts artifacts: "dist/**", fingerprint: true
            }
          },
          "wininst Release": {
            node(label: "Windows") {
              deleteDir()
              unstash "Source"
              bat "${env.PYTHON3} setup.py bdist_wininst"
              archiveArtifacts artifacts: "dist/**", fingerprint: true
            }
          }
        )
      }
    }
  }
}
