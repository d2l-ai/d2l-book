stage("Build and Publish") {
  node {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''#!/bin/bash
      set -ex
      rm -rf env
      python setup.py install
      source activate env/bin/activate
      cd demo
      d2lbook build html pdf
      '''

      if (env.BRANCH_NAME == 'master') {
        sh '''#!/bin/bash
        source activate env/bin/activate
        d2lbook deploy html pdf
      '''
      }
    }
  }
}
