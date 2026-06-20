pipeline {
    agent any

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Code Linting & Static Analysis') {
            steps {
                echo 'Running python syntax and lint checks...'
                sh 'find . -name "*.py" -not -path "*/.*" | xargs python3 -m py_compile'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker build -t telemetry-services ./telemetry-service'
                sh 'docker build -t ai-service ./ai-service'
                sh 'docker build -t dashboard-service ./dashboard-service'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh 'kubectl apply -f kubernetes/'
            }
        }
    }
}