<template>
  <li>
    <div>
      <i class="fas text-gray-300 fa-1fourx fa-plus-circle activity-icon"></i>
      <div class="media">
        <div class="media-left">
          <a href="#">
            <img class="media-object rounded-circle" :src="action.user.avatarUrl" alt="Avatar">
          </a>
        </div>
        <div class="media-body">
          {{ action.occurredAt | moment("from", "now") }}
        </div>
        <span class="card-text"><a href="#">{{ action.user.firstname }} {{ action.user.surname }}</a> {{ action.text }}</span>
      </div>
    </div>
  </li>
</template>

<script>
export default {
  name: 'Activity',
  props: {
    action: Object
  }
}
</script>
