pipeline {
  agent any
  stages {
    stage('Unit Tests') {
      steps {
        sh 'ls'
        node(label: 'Windows') {
          checkout scm
          bat "${env.PYTHON3} setup.py test"
        }
        
      }
    }
  }
}