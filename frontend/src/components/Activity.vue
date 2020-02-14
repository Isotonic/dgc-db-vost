<template>
  <li>
    <div>
      <i class="fas text-gray-300 fa-1fourx fa-plus-circle activity-icon"></i>
      <div class="media">
        <div class="media-left">
          <i>
            <img class="media-object rounded-circle" :src="action.user.avatarUrl" alt="Avatar">
          </i>
        </div>
        <div class="media-body">
          {{ action.occurredAt | moment("from", "now") }}
        </div>
        <span class="card-text"><i>{{ action.user.firstname }} {{ action.user.surname }}</i> {{ action.text }}</span>
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
