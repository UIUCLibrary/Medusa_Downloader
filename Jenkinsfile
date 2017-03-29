pipeline {
  agent any
  stages {
    stage('Run Tests') {
      steps {
        sh 'ls'
        node(label: 'Windows') {
          bat '"${env.PYTHON3} setup.py test"'
        }
        
      }
    }
  }
}