<template>
  <li class="update-log">
    <div class="update-log-avatar">
      <a href="#">
        <img class="media-object rounded-circle" :src="comment.user.avatarUrl" alt="Avatar">
      </a>
      <div class="update-log-name text-muted">{{ comment.user.name }}</div>
    </div>
    <div class="update-log-text">
      <span class="d-block">{{ comment.text }}</span>
      <div class="update-body">{{ comment.sentAt | moment("from", "now") }}</div>
    </div>
  </li>
</template>

<script>
export default {
  name: 'Comment',
  props: {
    comment: Object
  }
}
</script>
