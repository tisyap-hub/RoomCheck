pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        AWS_DEFAULT_REGION = 'eu-north-1'
        ECR_REGISTRY = '199167114958.dkr.ecr.eu-north-1.amazonaws.com'
        ECR_REPOSITORY = 'roomcheck'
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm

                script {
                    def commit = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_URI =
                        "${env.ECR_REGISTRY}/${env.ECR_REPOSITORY}:${commit}-${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Build and Test') {
            steps {
                sh '''
                    docker run --rm \
                      --user "$(id -u):$(id -g)" \
                      -e HOME=/tmp \
                      -e PYTHONDONTWRITEBYTECODE=1 \
                      -v "$PWD:/app" \
                      -w /app \
                      python:3.14-slim \
                      sh -ec '
                        python -m venv /tmp/testenv
                        /tmp/testenv/bin/pip install --no-cache-dir -r requirements.txt
                        /tmp/testenv/bin/python database.py
                        /tmp/testenv/bin/python -m pytest -q -p no:cacheprovider
                      '
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t "$IMAGE_URI" .'
            }
        }

        stage('Push to ECR and Configure Pull Access') {
            steps {
                sh '''
                    set +x
                    umask 077
                    export DOCKER_CONFIG="$(mktemp -d)"
                    trap 'rm -rf "$DOCKER_CONFIG"' EXIT

                    aws ecr get-login-password \
                      > "$DOCKER_CONFIG/token"

                    docker login \
                      --username AWS \
                      --password-stdin "$ECR_REGISTRY" \
                      < "$DOCKER_CONFIG/token"

                    rm "$DOCKER_CONFIG/token"

                    docker push "$IMAGE_URI"

                    kubectl create secret generic ecr-registry \
                      --type=kubernetes.io/dockerconfigjson \
                      --from-file=.dockerconfigjson="$DOCKER_CONFIG/config.json" \
                      --dry-run=client -o yaml \
                      > "$DOCKER_CONFIG/pull-secret.yaml"

                    kubectl apply -f "$DOCKER_CONFIG/pull-secret.yaml"
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    sed "s|IMAGE_PLACEHOLDER|$IMAGE_URI|g" \
                      k8s/deployment.yaml > deployment-rendered.yaml

                    kubectl apply -f deployment-rendered.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl rollout status deployment/roomcheck \
                      --timeout=300s
                '''
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    kubectl get pods
                    kubectl get deployments
                    kubectl get services

                    kubectl exec deployment/roomcheck -- python -c \
                      "import urllib.request; print(urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=10).read().decode())"
                '''
            }
        }
    }

    post {
        failure {
            sh '''
                kubectl get pods || true
                kubectl describe pods -l app=roomcheck || true
                kubectl logs deployment/roomcheck --tail=80 || true
            '''
        }
    }
}
