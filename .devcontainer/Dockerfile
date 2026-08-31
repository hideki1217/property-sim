FROM ubuntu:latest

RUN apt update && apt-get --no-install-recommends install -y \
    build-essential \
    git wget curl ca-certificates

ARG UID
ARG GID
ARG USER_NAME
RUN set -eux; \
    # 既存ユーザー・グループを安全に削除
    if getent passwd "${UID}" >/dev/null; then \
        olduser=$(getent passwd "${UID}" | cut -d: -f1); \
        echo "UID ${UID} already used by ${olduser}, deleting..."; \
        userdel -r -f "${olduser}" || true; \
    fi; \
    if getent group "${GID}" >/dev/null; then \
        oldgroup=$(getent group "${GID}" | cut -d: -f1); \
        echo "GID ${GID} already used by ${oldgroup}, deleting..."; \
        groupdel "${oldgroup}" || true; \
    fi; \
    # 新規グループ・ユーザーを作成
    groupadd -g "${GID}" ${USER_NAME}; \
    useradd -m -u "${UID}" -g "${GID}" -s /bin/bash ${USER_NAME}; \
    # 念のためホーム権限を確認
    chown -R "${UID}:${GID}" /home/${USER_NAME}

USER ${USER_NAME}
WORKDIR /workspace

RUN wget -qO- https://astral.sh/uv/install.sh | sh
