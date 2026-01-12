pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
        VIRTUAL_ENV = 'venv'
    }
    
    stages {
        stage('Підготовка') {
            steps {
                echo 'Початок збірки проєкту...'
                sh 'python3 --version'
                sh 'pip3 --version'
            }
        }
        
        stage('Встановлення залежностей') {
            steps {
                echo 'Встановлення Python залежностей...'
                sh '''
                    python3 -m venv ${VIRTUAL_ENV}
                    . ${VIRTUAL_ENV}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Лінтинг коду') {
            steps {
                echo 'Перевірка якості коду...'
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    flake8 app.py --max-line-length=120 --statistics || true
                    pylint app.py --disable=C0103,C0114,C0115,C0116 || true
                '''
            }
        }
        
        stage('Форматування коду') {
            steps {
                echo 'Перевірка форматування...'
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    black --check app.py test_app.py || true
                '''
            }
        }
        
        stage('Модульні тести') {
            steps {
                echo 'Запуск unit тестів...'
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    pytest test_app.py -v --cov=app --cov-report=html --cov-report=term
                '''
            }
        }
        
        stage('Інтеграційні тести') {
            steps {
                echo 'Запуск інтеграційних тестів...'
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    python3 -m pytest test_app.py::TestAPIEndpoints -v
                '''
            }
        }
        
        stage('Збірка додатку') {
            steps {
                echo 'Збірка додатку...'
                sh '''
                    . ${VIRTUAL_ENV}/bin/activate
                    python3 -m py_compile app.py
                '''
            }
        }
        
        stage('Генерація звітів') {
            steps {
                echo 'Генерація звітів про покриття коду...'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Звіт покриття коду'
                ])
            }
        }
    }
    
    post {
        success {
            echo '✅ Збірка успішно завершена!'
            emailext (
                subject: "Успішна збірка: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Збірка проєкту успішно завершена.\n\nДеталі: ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            echo '❌ Збірка завершилась з помилками!'
            emailext (
                subject: "Невдала збірка: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Збірка проєкту завершилась з помилками.\n\nДеталі: ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        always {
            echo 'Очищення робочого середовища...'
            cleanWs()
        }
    }
}
