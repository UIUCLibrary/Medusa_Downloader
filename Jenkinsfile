pipeline {
  agent any
  stages {
    stage('Checkout') {
      agent any

        steps{
            checkout scm
            stash includes: '**', name: "Source", useDefaultExcludes: false
        }
    }
    stage('Unit Tests') {
      steps {
        sh 'ls'
        node(label: 'Windows') {
          unstash "Source"
          bat "${env.PYTHON3} setup.py test"
        }

      }
    }
  }
}
