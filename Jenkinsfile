stage("Build and Publish") {
  node {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''#!/bin/bash
      set -ex
      export PATH=~/miniconda3/bin:${PATH}
      which python
      which activate
      rm -rf env
      python -m venv env
      source activate env/bin/activate
      pip install .
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
