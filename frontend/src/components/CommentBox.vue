<template>
  <div class="editor">
    <editor-menu-bar :editor="editor" v-slot="{ commands, isActive, focused }">
      <div class="menubar" :class="{ 'is-focused': focused }">
        <button class="menubar__button" :class="{ 'is-active': isActive.bold() }" @click="commands.bold">
          <i class="fas fa-bold" />
        </button>
         <button class="menubar__button" :class="{ 'is-active': isActive.italic() }" @click="commands.italic">
          <i class="fas fa-italic" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.strike() }" @click="commands.strike">
          <i class="fas fa-strikethrough" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.underline() }" @click="commands.underline">
          <i class="fas fa-underline" />
        </button>
        <button class="menubar__button" @click="showImagePrompt(commands.image)">
          <i class="fas fa-image" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.code() }" @click="commands.code">
          <i class="fas fa-code" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.heading({ level: 1 }) }" @click="commands.heading({ level: 1 })">
          H1
        </button>
         <button class="menubar__button" :class="{ 'is-active': isActive.heading({ level: 2 }) }" @click="commands.heading({ level: 2 })">
          H2
        </button>
         <button class="menubar__button" :class="{ 'is-active': isActive.heading({ level: 3 }) }" @click="commands.heading({ level: 3 })">
          H3
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.bullet_list() }" @click="commands.bullet_list">
          <i class="fas fa-list" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.ordered_list() }" @click="commands.ordered_list">
          <i class="fas fa-list-ol" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.blockquote() }" @click="commands.blockquote">
          <i class="fas fa-quote-right" />
        </button>
        <button class="menubar__button" :class="{ 'is-active': isActive.code_block() }" @click="commands.code_block">
          <i class="fas fa-code" />
        </button>
        <button class="menubar__button" @click="commands.undo">
          <i class="fas fa-undo" />
        </button>
        <button class="menubar__button" @click="commands.redo">
          <i class="fas fa-redo" />
        </button>
      </div>
    </editor-menu-bar>
    <editor-content class="editor__content" :editor="editor">
    </editor-content>
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
    <editor-content :editor="editor" />
    <i class="fas fa-paper-plane float-right comment-icon" @click="addComment"></i>
  </div>
</template>

<script>
import { Editor, EditorContent, EditorMenuBar, EditorMenuBubble } from 'tiptap'
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
  Underline,
  History,
  Placeholder
} from 'tiptap-extensions'

export default {
  name: 'CommentBox',
  components: {
    EditorContent,
    EditorMenuBar,
    EditorMenuBubble
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
          new Underline(),
          new History(),
          new Placeholder({
            emptyNodeText: 'Add an update...'
          })
        ],
        content: ''
      }),
      linkUrl: null,
      linkMenuIsActive: false
    }
  },
  methods: {
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
    showImagePrompt: function (command) {
      const src = prompt('Enter the url of your image here')
      if (src !== null) {
        command({ src })
      }
    },
    addComment: function () {
      if (this.editor.getHTML() === '<p></p>') {
        return false
      }
      this.$emit('addComment', this.editor.getJSON())
    }
  },
  beforeDestroy () {
    this.editor.destroy()
  }
}
</script>
