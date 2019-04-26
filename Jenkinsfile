stage("Build and Publish") {
  node {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''#!/bin/bash
      set -ex
      rm -rf env
      pip install .
      source activate env/bin/activate
      cd demo
      d2lbook build html pdf
      d2lbook deploy html pdf
      '''
    }
  }
}
