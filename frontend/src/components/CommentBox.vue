<template>
  <div :class="['editor', editing ? 'mb-5' : '']">
    <editor-menu-bar :editor="editor" v-slot="{ commands, isActive, focused }">
      <div class="menubar" :class="{ 'is-focused': focused }">
        <button class="menubar__button" :class="{ 'is-active': isActive.bold() }" @click="commands.bold" v-tooltip="'Bold'">
          <i class="fas fa-bold" />
        </button>
         <button class="menubar__button" :class="{ 'is-active': isActive.italic() }" @click="commands.italic" v-tooltip="'Italic'">
          <i class="fas fa-italic" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.strike() }" @click="commands.strike" v-tooltip="'Strikethrough'">
          <i class="fas fa-strikethrough" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.underline() }" @click="commands.underline" v-tooltip="'Underline'">
          <i class="fas fa-underline" />
        </button>
        <input type="file" class="d-none" @change="fileUpload(commands.image)" ref="file" accept="image/*" />
        <button class="menubar__button" @click="$refs.file.click()" v-tooltip="'Upload Image'">
          <i class="fas fa-image" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.code() }" @click="commands.code" v-tooltip="'Code'">
          <i class="fas fa-code" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.heading({ level: 1 }) }" @click="commands.heading({ level: 1 })" v-tooltip="'Heading 1'">
          H1
        </button>
         <button class="menubar__button" :class="{ 'is-active': isActive.heading({ level: 2 }) }" @click="commands.heading({ level: 2 })" v-tooltip="'Heading 2'">
          H2
        </button>
         <button class="menubar__button" :class="{ 'is-active': isActive.heading({ level: 3 }) }" @click="commands.heading({ level: 3 })" v-tooltip="'Heading 3'">
          H3
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.bullet_list() }" @click="commands.bullet_list" v-tooltip="'Bullet List'">
          <i class="fas fa-list" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.ordered_list() }" @click="commands.ordered_list" v-tooltip="'Numbered List'">
          <i class="fas fa-list-ol" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.blockquote() }" @click="commands.blockquote" v-tooltip="'Quote'">
          <i class="fas fa-quote-right" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.code_block() }" @click="commands.code_block" v-tooltip="'Code block'">
          <i class="fas fa-code" />
        </button>
        <button v-if="hasTyped" class="menubar__button" @click="commands.undo" v-tooltip="'Undo'">
          <i class="fas fa-undo" />
        </button>
        <button v-if="hasTyped" class="menubar__button" @click="commands.redo" v-tooltip="'Redo'">
          <i class="fas fa-redo" />
        </button>
      </div>
    </editor-menu-bar>
    <editor-menu-bubble class="menububble" :editor="editor" @hide="hideLinkMenu" v-slot="{ commands, isActive, getMarkAttrs, menu }">
      <div class="menububble" :class="{ 'is-active': menu.isActive }" :style="`left: ${menu.left}px; bottom: ${menu.bottom}px;`">
        <form class="menububble__form" v-if="linkMenuIsActive" @submit.prevent="setLinkUrl(commands.link, linkUrl)">
          <input class="menububble__input" type="text" v-model="linkUrl" placeholder="https://" ref="linkInput" @keydown.esc="hideLinkMenu"/>
          <button class="menububble__button" @click="setLinkUrl(commands.link, null)" type="button">
          </button>
        </form>
        <template v-else>
          <button class="menububble__button" @click="showLinkMenu(getMarkAttrs('link'))" :class="{ 'is-active': isActive.link() }">
            <span>{{ isActive.link() ? 'Update Link' : 'Add Link'}}</span>
          </button>
        </template>
      </div>
    </editor-menu-bubble>
    <editor-content :class="['editor__content', 'edit-comment', submittedEmpty ? 'comment-box-empty' : '']" :editor="editor" />
    <i v-if="editing" class="fas fa-times float-right comment-cancel-icon" @click="cancelEdit" v-tooltip="'Cancel'"></i>
    <i :class="['fas', 'float-right', 'comment-icon', submittedEmpty ? 'comment-empty' : '', editing ? ['fa-check', 'hover'] : 'fa-paper-plane']" @click="submitComment" v-tooltip="editing ? 'Update' : 'Post'"></i>
  </div>
</template>

<script>
import _ from 'lodash'
import { Editor, EditorContent, EditorMenuBar, EditorMenuBubble } from 'tiptap'
import {
  Blockquote,
  CodeBlock,
  HardBreak,
  Heading,
  OrderedList,
  BulletList,
  ListItem,
  Bold,
  Code,
  Italic,
  Link,
  Strike,
  Underline,
  History,
  Placeholder
} from 'tiptap-extensions'

import Image from '@/utils/image'

export default {
  name: 'CommentBox',
  components: {
    EditorContent,
    EditorMenuBar,
    EditorMenuBubble
  },
  props: {
    editing: {
      type: Boolean,
      default: false
    },
    existingContent: {
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Add an update...'
    }
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
          new Bold(),
          new Code(),
          new Italic(),
          new Link(),
          new Image(),
          new Strike(),
          new Underline(),
          new History(),
          new Placeholder({
            emptyNodeText: this.placeholder
          })
        ],
        content: this.existingContent,
        onUpdate: () => {
          this.hasTyped = true
          this.submittedEmpty = false
        }
      }),
      linkUrl: null,
      linkMenuIsActive: false,
      hasTyped: false,
      submittedEmpty: false
    }
  },
  methods: {
    resetContent () {
      this.editor.setContent('')
    },
    showLinkMenu: function (attrs) {
      this.linkUrl = attrs.href
      this.linkMenuIsActive = true
      this.$nextTick(() => {
        this.$refs.linkInput.focus()
      })
    },
    hideLinkMenu: function () {
      this.linkUrl = null
      this.linkMenuIsActive = false
    },
    setLinkUrl: function (command, url) {
      command({ href: url })
      this.hideLinkMenu()
    },
    fileUpload: function (command) {
      const image = this.$refs.file.files[0]
      if (image !== null) {
        const reader = new FileReader()
        reader.onload = readerEvent => {
          const src = readerEvent.target.result
          command({ src })
        }
        reader.readAsDataURL(image)
      }
    },
    cancelEdit () {
      this.$emit('cancelEdit')
    },
    submitComment: function () {
      if (this.editor.getHTML() === '<p></p>' || _.isEqual(this.existingContent, this.editor.getJSON())) {
        this.submittedEmpty = true
      } else {
        if (this.editing) {
          this.$emit('editComment', this.editor)
        } else {
          this.$emit('submitComment', this.editor)
        }
      }
    }
  },
  beforeDestroy () {
    this.editor.destroy()
  }
}
</script>
