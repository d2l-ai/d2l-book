stage("Build and Publish") {
  node {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''#!/bin/bash
      set -ex
      export PATH=~/miniconda3/bin:${PATH}
      rm -rf ~/miniconda3/envs/d2l-book-build
      conda create --name d2l-book-build pip -y
      conda activate d2l-book-build
      pip install .
      cd demo
      pip install matplotlib numpy
      d2lbook build html pdf
      '''

      if (env.BRANCH_NAME == 'master') {
        sh '''#!/bin/bash
        set -ex
        export PATH=~/miniconda3/bin:${PATH}
        conda activate d2l-book-build
        d2lbook deploy html pdf
      '''
      }
    }
  }
}
