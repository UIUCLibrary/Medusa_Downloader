pipeline {
  agent any
  stages {
    stage('Run Tests') {
      steps {
        sh 'ls'
        node(label: 'Windows') {
          bat 'echo "Running tests"'
        }
        
      }
    }
  }
}