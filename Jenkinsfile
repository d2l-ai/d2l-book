stage("Build and Publish") {
  node {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''#!/bin/bash
      set -ex
      export PATH=~/miniconda3/bin:${PATH}
      conda create --name d2l-book-test
      source activate d2l-book-test
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
