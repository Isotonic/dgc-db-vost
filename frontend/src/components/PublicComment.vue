<template>
  <li class="update-log">
    <div class="update-log-text public">
      <editor-content class="editor__content" :editor="editor" />
      <div class="update-body">
        {{ comment.sentAt | moment("from", "now") }}
      </div>
    </div>
    <span v-if="comment.editedAt" class="text-xs font-weight-bold half-opacity float-right mt-1 mb-2">Edited {{ comment.editedAt | moment("from", "now") }}</span>
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
    setContent: function () {
      this.editor.setContent(this.parseText)
    }
  },
  computed: {
    parseText: function () {
      try {
        return JSON.parse(this.comment.text)
      } catch (_) {
        return this.comment.text
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
