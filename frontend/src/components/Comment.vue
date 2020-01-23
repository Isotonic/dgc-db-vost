<template>
  <li class="update-log">
    <div class="update-log-avatar">
      <a href="#">
        <img class="media-object rounded-circle" :src="comment.user.avatarUrl" alt="Avatar">
      </a>
      <div class="update-log-name text-muted">{{ comment.user.firstname }} {{ comment.user.surname }}</div>
    </div>
    <div class="update-log-text">
      <editor-content class="editor__content" :editor="editor" />
      <div class="update-body">{{ comment.sentAt | moment("from", "now") }}</div>
    </div>
  </li>
</template>

<script>
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

export default {
  name: 'Comment',
  components: {
    EditorContent
  },
  props: {
    comment: Object
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
      })
    }
  },
  methods: {
    parseText: function () {
      try {
        this.editor.setContent(JSON.parse(this.comment.text))
      } catch (_) {
        this.editor.setContent(this.comment.text)
      }
    }
  },
  created () {
    this.parseText()
  },
  beforeDestroy () {
    this.editor.destroy()
  }
}
</script>
