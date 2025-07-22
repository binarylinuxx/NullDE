-- =============================================
-- 1. BOOTSTRAP lazy.nvim
-- =============================================
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- =============================================
-- 2. CORE UI SETTINGS (Before plugins)
-- =============================================
vim.opt.termguicolors = true
vim.opt.showmode = false
vim.opt.laststatus = 3
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.cursorline = true
vim.opt.signcolumn = "yes"
vim.opt.colorcolumn = ""
vim.opt.fillchars = {
  vert = "│",
  fold = "⠀",
  eob = " ", -- suppress ~ at EndOfBuffer
  diff = "╱", -- alternatives = ⣿ ░ ─ ╱
  msgsep = "‾",
  foldopen = "▾",
  foldsep = "│",
  foldclose = "▸"
}

-- =============================================
-- 3. SETUP PLUGINS
-- =============================================
require("lazy").setup({
  -- Graphite theme
  {
  'binarylinuxx/graphite-nvim',
  config = function()
    vim.opt.background = "dark"
    vim.cmd.colorscheme("graphite")
  end,
  priority = 1000,
  },

  -- Enhanced Lualine with grayscale theme
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      -- Custom grayscale theme for lualine
      local graphite_theme = {
        normal = {
          a = { fg = '#EEEEEE', bg = '#4B4B4B', gui = 'bold' },
          b = { fg = '#D1D1D1', bg = '#3A3A3A' },
          c = { fg = '#A0A0A0', bg = '#2B2B2B' },
        },
        insert = {
          a = { fg = '#1E1E1E', bg = '#D1D1D1', gui = 'bold' },
          b = { fg = '#D1D1D1', bg = '#3A3A3A' },
          c = { fg = '#A0A0A0', bg = '#2B2B2B' },
        },
        visual = {
          a = { fg = '#1E1E1E', bg = '#B8B8B8', gui = 'bold' },
          b = { fg = '#D1D1D1', bg = '#3A3A3A' },
          c = { fg = '#A0A0A0', bg = '#2B2B2B' },
        },
        replace = {
          a = { fg = '#EEEEEE', bg = '#5C5C5C', gui = 'bold' },
          b = { fg = '#D1D1D1', bg = '#3A3A3A' },
          c = { fg = '#A0A0A0', bg = '#2B2B2B' },
        },
        command = {
          a = { fg = '#1E1E1E', bg = '#A0A0A0', gui = 'bold' },
          b = { fg = '#D1D1D1', bg = '#3A3A3A' },
          c = { fg = '#A0A0A0', bg = '#2B2B2B' },
        },
        inactive = {
          a = { fg = '#7E7E7E', bg = '#2B2B2B' },
          b = { fg = '#7E7E7E', bg = '#2B2B2B' },
          c = { fg = '#7E7E7E', bg = '#2B2B2B' },
        },
      }

      require('lualine').setup({
        options = {
          icons_enabled = true,
          theme = graphite_theme,
          component_separators = { left = '', right = ''},
          section_separators = { left = '', right = ''},
          disabled_filetypes = {
            statusline = {},
            winbar = {},
          },
          ignore_focus = {},
          always_divide_middle = true,
          globalstatus = true, -- Single statusline across all windows
          refresh = {
            statusline = 100,
            tabline = 100,
            winbar = 100,
          }
        },
        sections = {
          lualine_a = {'mode'},
          lualine_b = {
            'branch',
            {
              'diff',
              symbols = {added = '+', modified = '~', removed = '-'},
            },
            {
              'diagnostics',
              sources = {'nvim_diagnostic'},
              symbols = {error = 'E', warn = 'W', info = 'I', hint = 'H'},
            }
          },
          lualine_c = {
            {
              'filename',
              path = 1, -- Show relative path
              symbols = {
                modified = '[+]',
                readonly = '[RO]',
                unnamed = '[No Name]',
              }
            }
          },
          lualine_x = {
            'encoding',
            {
              'fileformat',
              symbols = {
                unix = 'LF',
                dos = 'CRLF',
                mac = 'CR',
              }
            },
            'filetype'
          },
          lualine_y = {'progress'},
          lualine_z = {'location'}
        },
        inactive_sections = {
          lualine_a = {},
          lualine_b = {},
          lualine_c = {{'filename', path = 1}},
          lualine_x = {'location'},
          lualine_y = {},
          lualine_z = {}
        },
        tabline = {},
        winbar = {},
        inactive_winbar = {},
        extensions = { "nvim-tree", "fugitive", "quickfix" }
      })
    end,
  },

  -- Better syntax highlighting
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter.configs").setup({
        ensure_installed = {
          "lua", "vim", "vimdoc", "query",
          "javascript", "typescript", "python", "rust", "go"
        },
        sync_install = false,
        auto_install = true,
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false,
        },
        indent = {
          enable = true
        },
      })
    end,
  },

  -- Better search highlighting
  {
    "nvim-lua/plenary.nvim", -- Required dependency
  },
  {
    "folke/todo-comments.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      require("todo-comments").setup({
        signs = true,
        sign_priority = 8,
        keywords = {
          FIX = { icon = "F", color = "error", alt = { "FIXME", "BUG", "FIXIT", "ISSUE" } },
          TODO = { icon = "T", color = "info" },
          HACK = { icon = "H", color = "warning" },
          WARN = { icon = "W", color = "warning", alt = { "WARNING", "XXX" } },
          PERF = { icon = "P", alt = { "OPTIM", "PERFORMANCE", "OPTIMIZE" } },
          NOTE = { icon = "N", color = "hint", alt = { "INFO" } },
          TEST = { icon = "T", color = "test", alt = { "TESTING", "PASSED", "FAILED" } },
        },
        gui_style = {
          fg = "NONE",
          bg = "BOLD",
        },
        merge_keywords = true,
        highlight = {
          multiline = true,
          multiline_pattern = "^.",
          multiline_context = 10,
          before = "",
          keyword = "wide",
          after = "fg",
          pattern = [[.*<(KEYWORDS)\s*:]],
          comments_only = true,
          max_line_len = 400,
          exclude = {},
        },
        colors = {
          error = { "#D1D1D1" },
          warning = { "#B8B8B8" },
          info = { "#A0A0A0" },
          hint = { "#7E7E7E" },
          default = { "#EEEEEE" },
          test = { "#D1D1D1" }
        },
        search = {
          command = "rg",
          args = {
            "--color=never",
            "--no-heading",
            "--with-filename",
            "--line-number",
            "--column",
          },
          pattern = [[\b(KEYWORDS):]], -- ripgrep regex
        },
      })
    end,
  },
})

-- =============================================
-- 4. ADDITIONAL UI ENHANCEMENTS
-- =============================================

-- Apply colorscheme after all plugins are loaded
vim.cmd.colorscheme("graphite")

-- Cursor settings for better visibility
vim.opt.guicursor = {
  "n-v-c:block-Cursor/lCursor-blinkon0",
  "i-ci:ver25-Cursor/lCursor",
  "r-cr:hor20-Cursor/lCursor"
}

-- Better window separators
vim.api.nvim_set_hl(0, "WinSeparator", { fg = "#4B4B4B", bg = "NONE" })

-- Enhanced search settings
vim.opt.hlsearch = true
vim.opt.incsearch = true
vim.opt.ignorecase = true
vim.opt.smartcase = true

-- Better completion menu
vim.opt.pumheight = 10
vim.opt.pumblend = 10

-- Folding
vim.opt.foldmethod = "expr"
vim.opt.foldexpr = "nvim_treesitter#foldexpr()"
vim.opt.foldenable = false -- Don't fold by default

-- Better indentation visibility
vim.opt.list = true
vim.opt.listchars = {
  tab = "→ ",
  trail = "·",
  extends = "›",
  precedes = "‹",
  nbsp = "·"
}

-- Disable background for terminal transparency support
vim.api.nvim_create_autocmd("ColorScheme", {
  pattern = "*",
  callback = function()
    -- Keep background for better readability, but you can uncomment these
    -- if you want transparency:
    -- vim.api.nvim_set_hl(0, "Normal", { bg = "NONE" })
    -- vim.api.nvim_set_hl(0, "NormalFloat", { bg = "NONE" })
    -- vim.api.nvim_set_hl(0, "SignColumn", { bg = "NONE" })
  end,
})
