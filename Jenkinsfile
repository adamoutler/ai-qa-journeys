pipeline {
    agent { label 'inferrence1' }
    parameters {
        // Allows you to dynamically select the project folder, defaulting to journeys/pastebin
        string(name: 'TARGET_PROJECT', defaultValue: 'journeys/pastebin', description: 'Which project folder to test')
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
                        env.DYNAMIC_TOKEN = sh(script: "openssl rand -base64 12", returnStdout: true).trim()
                        
                        def rootDir = pwd()
                        
                        // 1. Dump variables to .env so Docker Compose and Python can read them safely
                        sh """
                        echo "TARGET_PROJECT=${params.TARGET_PROJECT}" > .env
                        echo "RANDOM_TEXT=${env.RANDOM_TEXT}" >> .env
                        echo "DYNAMIC_TOKEN=${env.DYNAMIC_TOKEN}" >> .env
                        echo "KANBAN_API_KEY=${KANBAN_SECRET}" >> .env
                        echo "PROJECT_FROM_JENKINS=${params.PROJECT_FROM_JENKINS}" >> .env
                        """
                        
                        // 2. CD into the target project, pick 2 random journeys
                        // Security: Only copy the selected journeys to a temp folder for the container
                        sh """
                        rm -rf ${rootDir}/container_journeys ${rootDir}/.gemini_project
                        mkdir -p ${rootDir}/container_journeys ${rootDir}/.gemini_project
                        
                        cd ${params.TARGET_PROJECT}
                        find user-journies -name '*.md' | shuf -n 2 > ${rootDir}/selected-journeys-temp.txt
                        
                        while read journey; do
                            cp "\$journey" ${rootDir}/container_journeys/
                            basename "\$journey" >> ${rootDir}/selected-journeys.txt
                        done < ${rootDir}/selected-journeys-temp.txt
                        
                        cp .gemini/settings.json ${rootDir}/.gemini_project/
                        rm ${rootDir}/selected-journeys-temp.txt
                        """
                        
                        // 3. Spin up the container
                        timeout(time: 15, unit: 'MINUTES') {
                            sh 'docker compose up --abort-on-container-exit'
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            sh 'docker compose down -v'
            // Destroy the .env file and temp directories
            sh 'rm -rf .env selected-journeys.txt container_journeys .gemini_project'
        }
    }
}
