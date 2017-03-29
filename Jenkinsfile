pipeline {
  agent any
  stages {
    stage('Checkout') {
      agent any

        steps{
          step([$class: "wsCleanup"])
            checkout scm
            stash includes: '**', name: "Source", useDefaultExcludes: false
        }
    }
    stage('Unit Tests') {
      steps {
        node(label: 'Windows') {
          bat "dir"
          unstash "Source"
          bat "${env.PYTHON3} setup.py test"
        }

      }
    }
  }
}
