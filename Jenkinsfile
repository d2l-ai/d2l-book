stage("Build and Publish") {
  node('d2l-worker') {
    ws('workspace/d2l-book') {
      checkout scm
      sh '''set -ex
      conda remove -n d2l-book-build --all -y
      conda create -n d2l-book-build pip -y
      conda activate d2l-book-build
      pip install .
      python -m unittest d2lbook/*_test.py
      # pip install mypy
      # mypy --ignore-missing-imports d2lbook/*_test.py
      cd docs
      rm -rf _build
      pip install matplotlib numpy mypy
      d2lbook build eval
      d2lbook build eval --tab numpy
      d2lbook build eval --tab cpython
      d2lbook build pdf
      d2lbook build html --tab all
      '''

      if (env.BRANCH_NAME == 'master') {
        sh '''set -ex
        conda activate d2l-book-build
        cd docs
        d2lbook deploy html pdf
        d2lbook clear
      '''
      }
    }
  }
}
