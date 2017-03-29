pipeline {
  agent any
  stages {
    stage('Unit Tests') {
      steps {
        node(label: 'Windows') {
          bat "dir"
          bat "${env.PYTHON3} setup.py test"
        }

      }
    }
  }
}
