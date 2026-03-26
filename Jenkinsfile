pipeline {
    agent any
    parameters {
        // Allows you to dynamically select the project folder, defaulting to project1
        string(name: 'TARGET_PROJECT', defaultValue: 'pastebin', description: 'Which project folder to test')
        string(name: 'PROJECT_FROM_JENKINS', defaultValue: 'pastebin', description: 'Plane Workspace Slug')
    }
    triggers {
        cron('H 1 * * *') // Runs nightly around 1 AM
    }
    stages {
        stage('Execute Nightly AI QA') {
            steps {
                // Securely fetch the Kanban API Key from Jenkins Credentials
                withCredentials([string(credentialsId: 'plane-kanban-api-key', variable: 'KANBAN_SECRET')]) {
                    script {
                        env.RANDOM_TEXT = sh(script: "openssl rand -hex 8", returnStdout: true).trim()
                        
                        // 1. Dump variables to .env so Docker Compose and Python can read them safely
                        sh """
                        echo "TARGET_PROJECT=${params.TARGET_PROJECT}" > .env
                        echo "RANDOM_TEXT=${env.RANDOM_TEXT}" >> .env
                        echo "KANBAN_API_KEY=${KANBAN_SECRET}" >> .env
                        echo "PROJECT_FROM_JENKINS=${params.PROJECT_FROM_JENKINS}" >> .env
                        """
                        
                        // 2. CD into the target project, pick 2 random journeys, and save the relative paths
                        sh "cd ${params.TARGET_PROJECT} && find user-journies -name '*.md' | shuf -n 2 > ../selected-journeys.txt"
                        
                        // 3. Spin up the container
                        timeout(time: 15, unit: 'MINUTES') {
                            sh 'docker compose up --build --abort-on-container-exit'
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            sh 'docker compose down -v'
            // Destroy the .env file containing the API key immediately
            sh 'rm -f .env selected-journeys.txt'
        }
    }
}
  }
    }
}
