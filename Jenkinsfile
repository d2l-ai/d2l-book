stage("Build and Publish") {
  node {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''set -ex
      env
      echo ${EXECUTOR_NUMBER}
      echo ${env.EXECUTOR_NUMBER}
      '''

      if (env.BRANCH_NAME == 'master') {
        sh '''set -ex
        conda activate d2l-book-build
        cd demo
        d2lbook deploy html pdf
      '''
      }
    }
  }
}
