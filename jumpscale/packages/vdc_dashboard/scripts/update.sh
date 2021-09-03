#################
# Exit Code Number    Meaning
# 0                   Okay
# 64                  Error: poetry install failed                              POETRY_INSTALL_ERROR
# 65                  Error: hard reset files to HEAD failed                    GIT_RESET_ERROR
# 66                  Error: switch to the upstream branch failed               GIT_CHECKOUT_ERROR
# 67                  Error: can't find the branch name in the repository       GIT_BRANCH_NOT_EXIST
#################
POETRY_INSTALL_ERROR=64
GIT_RESET_ERROR=65
GIT_CHECKOUT_ERROR=66
GIT_BRANCH_NOT_EXIST=67

# fetching all remote branches"
git fetch --all

# setting the branch name to use on updating
if [ $1 ]; then SDK_BRANCH=$1; else SDK_BRANCH=development; fi
echo "we will use origin/${SDK_BRANCH} branch to update the code"

# find out if a remote git branch with $SDK_BRANCH name exists in the repository
if ! git show-ref --quiet --verify "refs/remotes/origin/$SDK_BRANCH"; then
  >&2 echo "error: can't find the branch <$SDK_BRANCH> in the repository"
  exit $GIT_BRANCH_NOT_EXIST
fi

# save the current information to use in case of update failure
SAVED_BRANCH_NAME=$(git branch --show-current)
SAVED_COMMIT_HASH=$(git log -1 --pretty=format:"%H")
echo "we will revert to $SAVED_BRANCH_NAME $SAVED_COMMIT_HASH in case of failure"

# checking if poetry.lock has changed
POETRY_INSTALL=false
if ! git diff --quiet origin/$SDK_BRANCH poetry.lock; then
  # They are differnet
  echo "poetry.lock has changed"
  POETRY_INSTALL=true
fi

git stash push jumpscale/packages/vdc_dashboard/package.toml

# git rid of the uncommited local changes and switch the branch
if ! git checkout -f $SDK_BRANCH; then
  >&2 echo "error: switch to the upstream branch <$SDK_BRANCH> failed"
  git stash pop
  exit $GIT_CHECKOUT_ERROR
fi

RESET_SUCCEEDED=false
if git reset --hard origin/$SDK_BRANCH; then
  RESET_SUCCEEDED=true
else
  ERR=$GIT_RESET_ERROR
  >&2 echo "Error: failed to hard reset files to HEAD"
fi

if $RESET_SUCCEEDED; then
  if $POETRY_INSTALL; then
    ERR=$POETRY_INSTALL_ERROR
    MAX_TRIES=4
    COUNT=0
    while [  $COUNT -lt $MAX_TRIES ]; do
        poetry install --no-interaction --no-dev
        if [ $? -eq 0 ];then
          git stash pop
          echo "Code updated and all defined dependencies successfully installed!"
          exit 0
        fi
    let COUNT=COUNT+1
    done
    >&2 echo "Error: Failed to install the defined dependencies!"
  else
    git stash pop
    echo "code updated successfully!"
    exit 0
  fi
fi

# reverting to saved info if hard reset files to HEAD or installing the defined dependencies was failed
git checkout -f $SAVED_BRANCH_NAME && git reset --hard $SAVED_COMMIT_HASH
git stash pop
exit $ERR
