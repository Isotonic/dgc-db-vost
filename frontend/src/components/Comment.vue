<template>
  <comment-box v-if="this.editor.options.editable" :editing="true" :existingContent="parseText" @cancelEdit="cancelEdit" @editComment="editComment" />
  <li v-else :class="['update-log', comment.editedAt ? 'update-edited-margin' : 'update-margin']">
    <div class="update-log-avatar">
      <i>
        <img class="media-object rounded-circle" :src="comment.user.avatarUrl" alt="Avatar">
      </i>
      <div class="update-log-name text-muted">{{ comment.user.firstname }} {{ comment.user.surname }}</div>
    </div>
    <div class="update-log-text">
      <editor-content class="editor__content" :editor="editor" />
      <div class="update-body">
        <i v-if="comment.public" class="fas fa-eye mr-1" v-tooltip="incident.public ? 'Viewable by the public' : 'Viewable by the public when incident is marked public'"></i>
        {{ comment.sentAt | moment("from", "now") }}
        <b-dropdown variant="link" size="xs" toggle-tag="div">
          <template slot="button-content">
              <i class="fas fa-ellipsis-v text-white ml-1"></i>
          </template>
          <b-dropdown-item v-if="isUsersComment" @click="editable">Edit update</b-dropdown-item>
          <social-sharing url="" :title="`[System Generated] ${publicName}\n${toText}\n${publicUrl}`" inline-template>
            <network network="twitter">
              <b-dropdown-item>Tweet update</b-dropdown-item>
            </network>
          </social-sharing>
          <b-dropdown-item v-if="hasPermission('mark_as_public')" @click="togglePublic">{{ comment.public ? 'Hide update from public' : 'Show update to public'}}</b-dropdown-item>
          <b-dropdown-item @click="isCommentQuestionModalVisible = true">Delete update</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>
    <span v-if="comment.editedAt" class="text-xs font-weight-bold half-opacity float-right mt-1 mb-2">Edited {{ comment.editedAt | moment("from", "now") }}</span>
    <question-modal v-if="isCommentQuestionModalVisible" v-show="isCommentQuestionModalVisible" :visible="isCommentQuestionModalVisible" :title="'Delete Update'" @btnAction="deleteComment" @close="isCommentQuestionModalVisible = false">
      <template v-slot:question>
        <div class="text-center">
          <span class="font-weight-bold">Are you sure you wish to delete this update?</span>
        </div>
      </template>
      <template v-slot:body>
        <div class="editor__content comment-public-text mt-3" v-html="editor.getHTML()" />
      </template>
    </question-modal>
  </li>
</template>

<script>
import router from '@/router/index'
import CommentBox from './CommentBox'
import QuestionModal from './modals/Question'

import { mapGetters } from 'vuex'
import { Editor, EditorContent } from 'tiptap'
import {
  Blockquote,
  CodeBlock,
  HardBreak,
  Heading,
  OrderedList,
  BulletList,
  ListItem,
  TodoItem,
  TodoList,
  Bold,
  Code,
  Italic,
  Image,
  Link,
  Strike,
  Underline
} from 'tiptap-extensions'

const htmlToText = require('html-to-text')

export default {
  name: 'Comment',
  components: {
    CommentBox,
    QuestionModal,
    EditorContent
  },
  props: {
    comment: Object,
    incident: Object
  },
  data () {
    return {
      editor: new Editor({
        extensions: [
          new Blockquote(),
          new CodeBlock(),
          new HardBreak(),
          new Heading({ levels: [1, 2, 3] }),
          new BulletList(),
          new OrderedList(),
          new ListItem(),
          new TodoItem({ nested: true }),
          new TodoList(),
          new Bold(),
          new Code(),
          new Italic(),
          new Link(),
          new Image(),
          new Strike(),
          new Underline()
        ],
        editable: false,
        content: ''
      }),
      isCommentQuestionModalVisible: false
    }
  },
  methods: {
    setContent: function () {
      this.editor.setContent(this.parseText)
    },
    editable: function () {
      this.editor.setOptions({
        editable: true
      })
      this.$emit('showCommentBox', false)
    },
    cancelEdit: function () {
      this.editor.setOptions({
        editable: false
      })
      this.$emit('showCommentBox', true)
    },
    editComment: function (editor) {
      this.cancelEdit()
      this.$emit('showCommentBox', true)
      this.ApiPut(`comments/${this.comment.id}`, { text: JSON.stringify(editor.getJSON()) })
    },
    deleteComment: function (modalAnswer) {
      this.isCommentQuestionModalVisible = false
      if (modalAnswer) {
        this.ApiDelete(`comments/${this.comment.id}`)
      }
    },
    togglePublic: function () {
      this.ApiPut(`comments/${this.comment.id}/public`, { public: !this.comment.public })
    }
  },
  computed: {
    parseText: function () {
      try {
        const comment = JSON.parse(this.comment.text)
        if (comment.type) {
          return comment
        }
        return this.comment.text
      } catch (_) {
        return this.comment.text
      }
    },
    toText: function () {
      return htmlToText.fromString(this.editor.getHTML(), { wordwrap: 0, uppercaseHeadings: true, noLinkBrackets: true })
    },
    isUsersComment: function () {
      const user = this.$store.getters['user/getUser']
      if (user && user.id === this.comment.user.id) {
        return true
      }
      return false
    },
    publicName: function () {
      return this.incident.publicName ? this.incident.publicName : this.incident.name
    },
    publicUrl: function () {
      return window.location.origin + '/' + router.resolve({ name: 'publicIncident', params: { incidentName: this.incident.name.replace(/ /g, '-'), incidentId: this.incident.id } }).href
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    })
  },
  watch: {
    comment: {
      deep: true,
      handler () {
        this.setContent()
      }
    }
  },
  created () {
    this.setContent()
  },
  beforeDestroy () {
    this.editor.destroy()
  }
}
</script>
