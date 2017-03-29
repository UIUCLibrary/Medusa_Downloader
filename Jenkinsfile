pipeline {
  agent any
  stages {
    stage('Unit Tests') {
      steps {
        node(label: 'Windows') {
          bat "${env.PYTHON3} setup.py testxml"
          junit 'reports/junit*.xml'
        }

      }
    }
  }
}
