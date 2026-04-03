# FSO vLLM Logic Vault
# Ingested Atomic Logic Units for the Neural Industry

VLLM_LOGIC_UNITS = [
    {
        "id": "kernel_warmup",
        "coords": [
            2,
            3,
            22
        ],
        "fiber": 27,
        "logic": "def kernel_warmup(worker: 'Worker'):\n    do_deep_gemm_warmup = envs.VLLM_USE_DEEP_GEMM and is_deep_gemm_supported() and (envs.VLLM_DEEP_GEMM_WARMUP != 'skip')\n    if do_deep_gemm_warmup:\n        model = worker.get_model()\n        max_tokens = worker.scheduler_config.max_num_batched_tokens\n        deep_gemm_warmup(model, max_tokens)\n    enable_flashinfer_autotune = worker.vllm_config.kernel_config.enable_flashinfer_autotune\n    if enable_flashinfer_autotune is False:\n        logger.info('Skipping FlashInfer autotune because it is disabled.')\n    elif has_flashinfer() and current_platform.has_device_capability(90):\n        flashinfer_autotune(worker.model_runner)\n\n    def _is_flashinfer_backend(backend):\n        try:\n            return backend.get_name() == 'FLASHINFER'\n        except NotImplementedError:\n            return False\n    if not worker.model_runner.is_pooling_model and worker.model_runner.attn_groups and all((_is_flashinfer_backend(group.backend) for groups in worker.model_runner.attn_groups for group in groups)):\n        logger.info('Warming up FlashInfer attention.')\n        worker.model_runner._dummy_run(num_tokens=16, skip_eplb=True, is_profile=True, force_attention=True, create_mixed_batch=True)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/warmup/kernel_warmup.py"
    },
    {
        "id": "create_whisper_attention_backend_with_block_pooling",
        "coords": [
            12,
            26,
            2
        ],
        "fiber": 9,
        "logic": "@functools.lru_cache\ndef create_whisper_attention_backend_with_block_pooling(underlying_attn_backend: AttentionBackend, block_pool_size: int) -> type[AttentionBackend]:\n    prefix = 'WhisperCausalAttentionWithBlockPooling_'\n    underlying_builder = underlying_attn_backend.get_builder_cls()\n    underlying_impl = underlying_attn_backend.get_impl_cls()\n\n    class WhisperCausalAttentionWithBlockPoolingBuilder(underlying_builder):\n\n        def __init__(self, kv_cache_spec: AttentionSpec, layer_names: list[str], vllm_config: VllmConfig, device: torch.device):\n            assert kv_cache_spec.num_kv_heads % block_pool_size == 0\n            kv_cache_spec = replace(kv_cache_spec, block_size=kv_cache_spec.block_size * block_pool_size, num_kv_heads=kv_cache_spec.num_kv_heads // block_pool_size)\n            super().__init__(kv_cache_spec, layer_names, vllm_config, device)\n            self.num_heads_kv = kv_cache_spec.num_kv_heads\n            self.headdim = kv_cache_spec.head_size\n            self.num_heads_q = kv_cache_spec.num_kv_heads\n\n        def build(self, common_prefix_len: int, common_attn_metadata: CommonAttentionMetadata, fast_build: bool=False) -> AttentionMetadata:\n            new_common_attn_metadata = copy.deepcopy(common_attn_metadata)\n            new_common_attn_metadata.query_start_loc *= block_pool_size\n            new_common_attn_metadata.query_start_loc_cpu *= block_pool_size\n            new_common_attn_metadata.seq_lens *= block_pool_size\n            if new_common_attn_metadata._seq_lens_cpu is not None:\n                new_common_attn_metadata._seq_lens_cpu *= block_pool_size\n            if new_common_attn_metadata._num_computed_tokens_cpu is not None:\n                new_common_attn_metadata._num_computed_tokens_cpu *= block_pool_size\n            new_common_attn_metadata.num_actual_tokens *= block_pool_size\n            new_common_attn_metadata.max_query_len *= block_pool_size\n            new_common_attn_metadata.max_seq_len *= block_pool_size\n            original_slot_mapping = common_attn_metadata.slot_mapping\n            common_prefix_len *= block_pool_size\n            new_common_attn_metadata.slot_mapping = (original_slot_mapping.unsqueeze(1) * block_pool_size + torch.arange(block_pool_size, device=original_slot_mapping.device)).flatten().clamp(min=-1)\n            return super().build(common_prefix_len, new_common_attn_metadata, fast_build)\n\n    class WhisperCausalAttentionWithBlockPoolingImpl(underlying_impl):\n\n        def forward(self, layer: torch.nn.Module, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, kv_cache: torch.Tensor, attn_metadata: AttentionMetadata, output: torch.Tensor | None=None, output_scale: torch.Tensor | None=None, output_block_scale: torch.Tensor | None=None) -> torch.Tensor:\n            if not underlying_attn_backend.forward_includes_kv_cache_update and attn_metadata is not None and (layer.kv_sharing_target_layer_name is None) and (key is not None) and (value is not None):\n                self.do_kv_cache_update(layer, key, value, kv_cache, attn_metadata.slot_mapping)\n            return super().forward(layer, query, key, value, kv_cache, attn_metadata, output, output_scale, output_block_scale)\n    _SUPPORTED_BACKENDS = tuple((b for b in (AiterFlashAttentionBackend, FlashAttentionBackend, RocmAttentionBackend, TritonAttentionBackend) if b is not None))\n    if not issubclass(underlying_attn_backend, _SUPPORTED_BACKENDS):\n        raise NotImplementedError(f'{underlying_attn_backend} is not yet supported.Contributions to support more backends are much appreciated.')\n    if not issubclass(underlying_attn_backend, FlashAttentionBackend):\n        logger.info('Using %s for Whisper causal attention with block pooling. This backend was recently enabled for this model. If you encounter any accuracy or performance issues, please open an issue at https://github.com/vllm-project/vllm/issues with the [ROCm] tag so it can be triaged by the appropriate team.', underlying_attn_backend.get_name())\n    attn_backend = subclass_attention_backend_with_overrides(name_prefix=prefix, attention_backend_cls=underlying_attn_backend, overrides={'get_builder_cls': lambda: WhisperCausalAttentionWithBlockPoolingBuilder, 'get_impl_cls': lambda: WhisperCausalAttentionWithBlockPoolingImpl, 'get_kv_cache_shape': lambda num_blocks, block_size, num_kv_heads, head_size, cache_dtype_str: underlying_attn_backend.get_kv_cache_shape(num_blocks, block_size * block_pool_size, num_kv_heads // block_pool_size, head_size, cache_dtype_str), 'forward_includes_kv_cache_update': True})\n    return attn_backend",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/whisper_causal.py"
    },
    {
        "id": "_create_patch_attention_mask",
        "coords": [
            0,
            4,
            9
        ],
        "fiber": 13,
        "logic": "def _create_patch_attention_mask(self, pixel_mask: torch.Tensor | None) -> torch.Tensor | None:\n    if pixel_mask is None:\n        return None\n    patches_subgrid = pixel_mask.unfold(dimension=1, size=self.vision_tower.config.patch_size, step=self.vision_tower.config.patch_size).unfold(dimension=2, size=self.vision_tower.config.patch_size, step=self.vision_tower.config.patch_size)\n    return (patches_subgrid.sum(dim=(-1, -2)) > 0).bool()",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/aria.py"
    },
    {
        "id": "self_attention",
        "coords": [
            8,
            19,
            28
        ],
        "fiber": 24,
        "logic": "def self_attention(self, positions: torch.Tensor, hidden_states: torch.Tensor, **kwargs) -> torch.Tensor:\n    qkv, _ = self.qkv_proj(hidden_states)\n    q, k, v = qkv.split([self.q_size, self.kv_size, self.kv_size], dim=-1)\n    k = k * self.key_multiplier\n    q, k = self.rotary_emb(positions, q, k)\n    attn_output = self.attn(q, k, v)\n    output, _ = self.o_proj(attn_output)\n    return output",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/falcon_h1.py"
    },
    {
        "id": "forward_attention",
        "coords": [
            6,
            13,
            27
        ],
        "fiber": 15,
        "logic": "def forward_attention(self, attn: torch.Tensor, v: torch.Tensor, mask: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor]:\n    if mask is not None:\n        mask = mask.unsqueeze(1)\n        mask = mask.eq(0)\n        attn = attn.masked_fill(mask, -float('inf'))\n        attn = torch.softmax(attn, dim=-1).masked_fill(mask, 0.0)\n    else:\n        attn = torch.softmax(attn, dim=-1)\n    d_attn = attn\n    output = torch.matmul(d_attn, v)\n    return (output, attn)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/fireredasr2.py"
    },
    {
        "id": "self_attention",
        "coords": [
            8,
            19,
            28
        ],
        "fiber": 24,
        "logic": "def self_attention(self, positions: torch.Tensor, hidden_states: torch.Tensor, **kwargs) -> torch.Tensor:\n    qkv, _ = self.qkv_proj(hidden_states)\n    q, k, v = qkv.split([self.q_size, self.kv_size, self.kv_size], dim=-1)\n    q, k = self.rotary_emb(positions, q, k)\n    attn_output = self.attn(q, k, v)\n    output, _ = self.o_proj(attn_output)\n    return output",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/bamba.py"
    },
    {
        "id": "is_attention_free",
        "coords": [
            25,
            5,
            11
        ],
        "fiber": 10,
        "logic": "@overload\ndef is_attention_free(model: object) -> TypeIs[IsAttentionFree]:\n    ...",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/interfaces.py"
    },
    {
        "id": "is_attention_free",
        "coords": [
            25,
            5,
            11
        ],
        "fiber": 10,
        "logic": "@overload\ndef is_attention_free(model: type[object]) -> TypeIs[type[IsAttentionFree]]:\n    ...",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/interfaces.py"
    },
    {
        "id": "is_attention_free",
        "coords": [
            25,
            5,
            11
        ],
        "fiber": 10,
        "logic": "def is_attention_free(model: type[object] | object) -> TypeIs[type[IsAttentionFree]] | TypeIs[IsAttentionFree]:\n    return getattr(model, 'is_attention_free', False)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/interfaces.py"
    },
    {
        "id": "_bilinear_pos_embed_kernel",
        "coords": [
            29,
            24,
            7
        ],
        "fiber": 29,
        "logic": "@triton.jit\ndef _bilinear_pos_embed_kernel(embed_ptr, output_ptr, H, W, h_scale, w_scale, NUM_GRID: tl.constexpr, M_SIZE: tl.constexpr, HIDDEN_DIM: tl.constexpr, BLOCK_D: tl.constexpr):\n    \"\"\"Fused bilinear pos-embed interpolation with spatial-merge reorder.\"\"\"\n    pid = tl.program_id(0)\n    total_spatial = H * W\n    spatial_idx = pid % total_spatial\n    num_blocks_w = W // M_SIZE\n    block_idx = spatial_idx // (M_SIZE * M_SIZE)\n    local_idx = spatial_idx % (M_SIZE * M_SIZE)\n    br = block_idx // num_blocks_w\n    bc = block_idx % num_blocks_w\n    lr = local_idx // M_SIZE\n    lc = local_idx % M_SIZE\n    row = br * M_SIZE + lr\n    col = bc * M_SIZE + lc\n    h_frac = row.to(tl.float32) * h_scale\n    w_frac = col.to(tl.float32) * w_scale\n    hf = tl.math.floor(h_frac).to(tl.int32)\n    wf = tl.math.floor(w_frac).to(tl.int32)\n    hc = tl.minimum(hf + 1, NUM_GRID - 1)\n    wc = tl.minimum(wf + 1, NUM_GRID - 1)\n    dh = h_frac - hf.to(tl.float32)\n    dw = w_frac - wf.to(tl.float32)\n    w11 = dh * dw\n    w10 = dh - w11\n    w01 = dw - w11\n    w00 = 1.0 - dh - w01\n    off00 = (hf * NUM_GRID + wf) * HIDDEN_DIM\n    off01 = (hf * NUM_GRID + wc) * HIDDEN_DIM\n    off10 = (hc * NUM_GRID + wf) * HIDDEN_DIM\n    off11 = (hc * NUM_GRID + wc) * HIDDEN_DIM\n    out_off = pid * HIDDEN_DIM\n    out_dtype = output_ptr.dtype.element_ty\n    w00_c = w00.to(out_dtype)\n    w01_c = w01.to(out_dtype)\n    w10_c = w10.to(out_dtype)\n    w11_c = w11.to(out_dtype)\n    for d in tl.range(0, HIDDEN_DIM, BLOCK_D):\n        cols = d + tl.arange(0, BLOCK_D)\n        mask = cols < HIDDEN_DIM\n        e00 = tl.load(embed_ptr + off00 + cols, mask=mask)\n        e01 = tl.load(embed_ptr + off01 + cols, mask=mask)\n        e10 = tl.load(embed_ptr + off10 + cols, mask=mask)\n        e11 = tl.load(embed_ptr + off11 + cols, mask=mask)\n        val = w00_c * e00 + w01_c * e01 + w10_c * e10 + w11_c * e11\n        tl.store(output_ptr + out_off + cols, val, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/qwen3_vl.py"
    },
    {
        "id": "self_attention",
        "coords": [
            8,
            19,
            28
        ],
        "fiber": 24,
        "logic": "def self_attention(self, positions: torch.Tensor, hidden_states: torch.Tensor, **kwargs) -> torch.Tensor:\n    qkv, _ = self.qkv_proj(hidden_states)\n    q, k, v = qkv.split([self.q_size, self.kv_size, self.kv_size], dim=-1)\n    attn_output = self.attn(q, k, v)\n    output, _ = self.o_proj(attn_output)\n    return output",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/jamba.py"
    },
    {
        "id": "dummy_attention",
        "coords": [
            1,
            11,
            28
        ],
        "fiber": 9,
        "logic": "@maybe_transfer_kv_layer\ndef dummy_attention(layer_name, _placeholder):\n    return _placeholder",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/extract_hidden_states.py"
    },
    {
        "id": "use_cascade_attention",
        "coords": [
            4,
            20,
            1
        ],
        "fiber": 25,
        "logic": "@staticmethod\ndef use_cascade_attention(*args, **kwargs) -> bool:\n    return False",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/extract_hidden_states.py"
    },
    {
        "id": "fused_olmo_hybrid_gdn_gating_kernel",
        "coords": [
            6,
            19,
            7
        ],
        "fiber": 1,
        "logic": "@triton.jit\ndef fused_olmo_hybrid_gdn_gating_kernel(g, beta_output, A_log, a, b, dt_bias, seq_len, allow_neg_eigval: tl.constexpr, NUM_HEADS: tl.constexpr, beta: tl.constexpr, threshold: tl.constexpr, BLK_HEADS: tl.constexpr):\n    i_b, i_s, i_d = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    head_off = i_d * BLK_HEADS + tl.arange(0, BLK_HEADS)\n    off = i_b * seq_len * NUM_HEADS + i_s * NUM_HEADS + head_off\n    mask = head_off < NUM_HEADS\n    blk_A_log = tl.load(A_log + head_off, mask=mask)\n    blk_a = tl.load(a + off, mask=mask)\n    blk_b = tl.load(b + off, mask=mask)\n    blk_bias = tl.load(dt_bias + head_off, mask=mask)\n    x = blk_a.to(tl.float32) + blk_bias.to(tl.float32)\n    softplus_x = tl.where(beta * x <= threshold, 1 / beta * tl.log(1 + tl.exp(beta * x)), x)\n    blk_g = -tl.exp(blk_A_log.to(tl.float32)) * softplus_x\n    tl.store(g + off, blk_g.to(g.dtype.element_ty), mask=mask)\n    blk_beta_output = tl.sigmoid(blk_b.to(tl.float32))\n    if allow_neg_eigval:\n        blk_beta_output = blk_beta_output * 2.0\n    tl.store(beta_output + off, blk_beta_output.to(beta_output.dtype.element_ty), mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/olmo_hybrid.py"
    },
    {
        "id": "get_attention_mask_by_audio_len",
        "coords": [
            5,
            26,
            28
        ],
        "fiber": 28,
        "logic": "def get_attention_mask_by_audio_len(self, audio_lens: torch.Tensor | None, hidden_states: torch.Tensor):\n    \"\"\"\n        Create attention mask based on audio lengths to mask out padding tokens\n        For each sample in batch:\n        - Convert raw audio length to feature length after convolutions\n        - Create bool mask: True for valid positions and False for padding\n        - Convert to attention mask format expected by transformer layers\n        (1.0 for positions to attend to, large negative for positions to ignore)\n        This masking ensures consistent behavior between training and inference\n        by preventing the model from attending to padding tokens in both cases\n        \"\"\"\n    if audio_lens is None:\n        return None\n    audio_feature_len = self._get_feat_extract_output_lengths(audio_lens)\n    max_seq_len = hidden_states.shape[1]\n    attention_mask = torch.arange(max_seq_len, device=hidden_states.device)[None, :].lt(audio_feature_len.view(-1, 1))\n    attention_mask = self.get_extended_attention_mask(attention_mask, None, dtype=hidden_states.dtype)\n    return attention_mask",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/ultravox.py"
    },
    {
        "id": "forward_attention",
        "coords": [
            6,
            13,
            27
        ],
        "fiber": 15,
        "logic": "def forward_attention(self, value: torch.Tensor, scores: torch.Tensor, mask: torch.Tensor, mask_att_chunk_encoder: torch.Tensor=None):\n    n_batch = value.size(0)\n    if mask is not None:\n        if mask_att_chunk_encoder is not None:\n            mask = mask * mask_att_chunk_encoder\n        mask = mask.unsqueeze(1).eq(0)\n        min_value = -float('inf')\n        scores = scores.masked_fill(mask, min_value)\n        attn = torch.softmax(scores, dim=-1).masked_fill(mask, 0.0)\n    else:\n        attn = torch.softmax(scores, dim=-1)\n    p_attn = attn\n    x = torch.matmul(p_attn, value)\n    x = x.transpose(1, 2).contiguous().view(n_batch, -1, self.h * self.d_k)\n    out, _ = self.out_proj(x)\n    return out",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/funasr.py"
    },
    {
        "id": "_reshape_for_broadcast",
        "coords": [
            8,
            9,
            24
        ],
        "fiber": 10,
        "logic": "def _reshape_for_broadcast(freqs_cis: torch.Tensor, x: torch.Tensor) -> torch.Tensor:\n    \"\"\"\n    freqs_cis: complex - (seq_len, head_dim / 2)\n    x: complex - (bsz, seq_len, head_dim / 2)\n    \"\"\"\n    ndim = x.ndim\n    assert ndim > 1\n    assert freqs_cis.shape == (x.shape[1], x.shape[-1]), (freqs_cis.shape, (x.shape[1], x.shape[-1]))\n    shape = [d if i == 1 or i == ndim - 1 else 1 for i, d in enumerate(x.shape)]\n    return freqs_cis.view(*shape)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/pixtral.py"
    },
    {
        "id": "is_attention_free_model",
        "coords": [
            22,
            15,
            18
        ],
        "fiber": 24,
        "logic": "def is_attention_free_model(self, architectures: str | list[str], model_config: ModelConfig) -> bool:\n    model_cls, _ = self.inspect_model_cls(architectures, model_config)\n    return model_cls.is_attention_free",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/registry.py"
    },
    {
        "id": "_handle_expert_scale_broadcasting",
        "coords": [
            28,
            16,
            5
        ],
        "fiber": 18,
        "logic": "def _handle_expert_scale_broadcasting(self, weights: list[tuple[str, torch.Tensor]], params_dict: dict) -> tuple[list[tuple[str, torch.Tensor]], set[str]]:\n    \"\"\"Handle expert scale parameters that need broadcasting.\n\n        ModelOpt checkpoints use a single value tensor scalar for BMM style\n        experts, vLLM expects the scale to be broadcasted across all experts.\n        \"\"\"\n    regular_weights = []\n    expert_scale_weights = []\n    updated_params = set()\n    for name, weight in weights:\n        if 'feed_forward.experts.' in name and 'scale' in name and ('.shared_expert' not in name):\n            if name in params_dict:\n                param = params_dict[name]\n                if hasattr(param, 'data') and param.data.numel() > 1 and (weight.numel() == 1):\n                    param.data.fill_(weight.item())\n                    updated_params.add(name)\n                    continue\n            expert_scale_weights.append((name, weight))\n        else:\n            regular_weights.append((name, weight))\n    return (regular_weights, expert_scale_weights, updated_params)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/mllama4.py"
    },
    {
        "id": "forward_attention",
        "coords": [
            6,
            13,
            27
        ],
        "fiber": 15,
        "logic": "def forward_attention(self, value: torch.Tensor, scores: torch.Tensor, mask: torch.Tensor | None) -> torch.Tensor:\n    \"\"\"Compute attention context vector.\n        Args:\n            value (torch.Tensor): (batch, time2, size)\n            scores(torch.Tensor): (batch, time1, time2)\n            mask(torch.Tensor): (batch, time1, time2)\n        returns:\n            value (torch.Tensor): transformed `value`\n                (batch, time2, d_model) weighted by the\n                attention scores\n        \"\"\"\n    n_batch = value.size(0)\n    if mask is not None:\n        mask = mask.unsqueeze(1)\n        scores = scores.masked_fill(mask, -INF_VAL)\n        attn = torch.softmax(scores, dim=-1).masked_fill(mask, 0.0)\n    else:\n        attn = torch.softmax(scores, dim=-1)\n    x = torch.matmul(attn, value)\n    x = x.transpose(1, 2).reshape(n_batch, -1, self.h * self.d_k)\n    return self.linear_out(x)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/cohere_asr.py"
    },
    {
        "id": "attention_qkvpacked",
        "coords": [
            30,
            12,
            21
        ],
        "fiber": 1,
        "logic": "def attention_qkvpacked(self, x: torch.Tensor, cu_seqlens: torch.Tensor, rope_freqs_cis: torch.Tensor | None=None):\n    \"\"\"\n        Args:\n            x (torch.Tensor): (seqlen, hidden_dim)\n            cu_seqlens (torch.Tensor):\n        \"\"\"\n    seq_length = x.size(0)\n    xqkv, _ = self.wqkv(x)\n    qkv_shape = xqkv.size()[:-1] + (3, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)\n    xqkv = xqkv.view(*qkv_shape)\n    xq, xk, xv = torch.unbind(xqkv, dim=-3)\n    xq, xk = apply_rope(xq, xk, rope_freqs_cis)\n    max_seqlen = (cu_seqlens[1:] - cu_seqlens[:-1]).max()\n    attn_out = self.attn(xq.unsqueeze(0), xk.unsqueeze(0), xv.unsqueeze(0), cu_seqlens=cu_seqlens, max_seqlen=max_seqlen)\n    attn_out = attn_out.reshape(seq_length, self.num_attention_heads_per_partition * self.hidden_size_per_attention_head)\n    attn_out, _ = self.wo(attn_out)\n    return attn_out",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/moonvit.py"
    },
    {
        "id": "attention_qkvpacked",
        "coords": [
            30,
            12,
            21
        ],
        "fiber": 1,
        "logic": "def attention_qkvpacked(self, x: torch.Tensor, cu_seqlens: torch.Tensor, rope_freqs_cis: torch.Tensor | None=None):\n    \"\"\"Compute self-attention with packed QKV.\n\n        Args:\n            x (torch.Tensor): (seqlen, hidden_dim)\n            cu_seqlens (torch.Tensor): cumulative sequence lengths\n        \"\"\"\n    seq_length = x.size(0)\n    xqkv, _ = self.wqkv(x)\n    qkv_shape = xqkv.size()[:-1] + (3, self.num_attention_heads_per_partition, self.hidden_size_per_attention_head)\n    xqkv = xqkv.view(*qkv_shape)\n    xq, xk, xv = torch.unbind(xqkv, dim=-3)\n    xq, xk = apply_rope(xq, xk, rope_freqs_cis)\n    max_seqlen = (cu_seqlens[1:] - cu_seqlens[:-1]).max()\n    attn_out = self.attn(xq.unsqueeze(0), xk.unsqueeze(0), xv.unsqueeze(0), cu_seqlens=cu_seqlens, max_seqlen=max_seqlen)\n    attn_out = attn_out.reshape(seq_length, self.num_attention_heads_per_partition * self.hidden_size_per_attention_head)\n    attn_out, _ = self.wo(attn_out)\n    return attn_out",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/kimi_k25_vit.py"
    },
    {
        "id": "_build_audio_encoder_attention_mask",
        "coords": [
            12,
            21,
            25
        ],
        "fiber": 27,
        "logic": "def _build_audio_encoder_attention_mask(feature_attention_mask: torch.Tensor, *, dtype: torch.dtype, device: torch.device) -> torch.Tensor:\n    input_lengths = feature_attention_mask.sum(-1).to(torch.long)\n    conv_lengths = (input_lengths - 1) // 2 + 1\n    batch_size, max_mel_seq_len = feature_attention_mask.shape\n    max_seq_len = (max_mel_seq_len - 1) // 2 + 1\n    seq_range = torch.arange(max_seq_len, dtype=conv_lengths.dtype, device=conv_lengths.device).unsqueeze(0).expand(batch_size, max_seq_len)\n    padding_mask = seq_range >= conv_lengths[:, None]\n    attention_mask = padding_mask.view(batch_size, 1, 1, max_seq_len).expand(batch_size, 1, max_seq_len, max_seq_len)\n    attention_mask = attention_mask.to(dtype=dtype, device=device)\n    attention_mask.masked_fill_(padding_mask[:, None, None, :], float('-inf'))\n    return attention_mask",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/audioflamingo3.py"
    },
    {
        "id": "init_relative_attention_bias",
        "coords": [
            2,
            27,
            14
        ],
        "fiber": 12,
        "logic": "def init_relative_attention_bias(self, input_tensor: torch.Tensor) -> torch.Tensor | None:\n    if self.relative_attention_bias_layer:\n        return self.relative_attention_bias_layer(input_tensor)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/phi4mm_audio.py"
    },
    {
        "id": "add_and_maybe_inplace_all_reduce",
        "coords": [
            27,
            29,
            3
        ],
        "fiber": 28,
        "logic": "def add_and_maybe_inplace_all_reduce(self, in1: torch.Tensor, in2: torch.Tensor) -> torch.Tensor:\n    if not self.use_fused_all_reduce:\n        return in1 + in2\n    return self.tp_group.all_reduce(in1 + in2)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/step3p5.py"
    },
    {
        "id": "attention",
        "coords": [
            28,
            19,
            10
        ],
        "fiber": 26,
        "logic": "def attention(self, x: torch.Tensor, attn_mask: torch.Tensor | None=None) -> torch.Tensor:\n    attn_mask = attn_mask.to(x.dtype) if attn_mask is not None else None\n    return self.attn(x, attn_mask=attn_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/qwen_vl.py"
    },
    {
        "id": "_prepare_attention_mask",
        "coords": [
            29,
            3,
            18
        ],
        "fiber": 19,
        "logic": "def _prepare_attention_mask(self, inputs_tensor: torch.Tensor, cu_seqlens: torch.Tensor) -> torch.Tensor | None:\n    if getattr(self.config, '_attn_implementation', 'eager') == 'flash_attention_2':\n        return None\n    seq_length = inputs_tensor.shape[0]\n    attention_mask = torch.full((1, 1, seq_length, seq_length), torch.finfo(inputs_tensor.dtype).min, device=inputs_tensor.device, dtype=inputs_tensor.dtype)\n    for i in range(1, len(cu_seqlens)):\n        start = int(cu_seqlens[i - 1].item())\n        end = int(cu_seqlens[i].item())\n        attention_mask[..., start:end, start:end] = 0\n    return attention_mask",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/funaudiochat.py"
    },
    {
        "id": "add_all_reduce",
        "coords": [
            11,
            1,
            0
        ],
        "fiber": 12,
        "logic": "def add_all_reduce(mlp: nn.Module):\n    \"\"\"Adds an all-reduce to the output of `mlp.forward()`.\"\"\"\n\n    class MLPWithAllReduce(mlp.__class__):\n\n        def forward(self, *args, **kwargs):\n            output = super().forward(*args, **kwargs)\n            return self.experts.maybe_all_reduce_tensor_model_parallel(output)\n    mlp.__class__ = MLPWithAllReduce",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/transformers/moe.py"
    },
    {
        "id": "vllm_flash_attention_forward",
        "coords": [
            18,
            2,
            2
        ],
        "fiber": 22,
        "logic": "def vllm_flash_attention_forward(module: torch.nn.Module, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, attention_mask: torch.Tensor, scaling: float | None=None, attention_instances: dict[int, Attention] | None=None, **kwargs):\n    self_attn = attention_instances[module.layer_idx]\n    if scaling is not None:\n        self_attn.impl.scale = float(scaling)\n    hidden = query.shape[-2]\n    query, key, value = (x.transpose(1, 2) for x in (query, key, value))\n    query, key, value = (x.reshape(hidden, -1) for x in (query, key, value))\n    return (self_attn.forward(query, key, value), None)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/transformers/base.py"
    },
    {
        "id": "create_attention_instances",
        "coords": [
            1,
            9,
            0
        ],
        "fiber": 10,
        "logic": "def create_attention_instances(self) -> dict[int, Attention]:\n    \"\"\"\n        Create `Attention` instances to inform KV cache allocation.\n        \"\"\"\n    text_config = self.text_config\n    num_heads = self.model_config.get_num_attention_heads(self.parallel_config)\n    head_size = self.model_config.get_head_size()\n    num_kv_heads = self.model_config.get_num_kv_heads(self.parallel_config)\n    logits_soft_cap = getattr(text_config, 'attn_logit_softcapping', None)\n    is_encoder = lambda module: not getattr(module, 'is_causal', True)\n    has_encoder = lambda model: any((is_encoder(m) for m in model.modules()))\n    is_multimodal = lambda config: config != config.get_text_config()\n    if has_encoder(self.model) and (not is_multimodal(self.config)):\n        self.check_version('5.0.0', 'encoder models support')\n        attn_type = AttentionType.ENCODER_ONLY\n    else:\n        attn_type = AttentionType.DECODER\n    pp_rank = self.pp_group.rank_in_group\n    pp_size = self.pp_group.world_size\n    start, end = get_pp_indices(text_config.num_hidden_layers, pp_rank, pp_size)\n    attention_instances = {}\n    for i in range(start, end):\n        per_layer_sliding_window = None\n        if hasattr(self.config, 'layer_types') and self.config.layer_types[i] == 'sliding_attention':\n            per_layer_sliding_window = self.config.sliding_window\n        attn_cls = EncoderOnlyAttention if attn_type == AttentionType.ENCODER_ONLY else Attention\n        attention_instances[i] = attn_cls(num_heads=num_heads, head_size=head_size, scale=head_size ** (-0.5), num_kv_heads=num_kv_heads, cache_config=self.cache_config, quant_config=self.quant_config, logits_soft_cap=logits_soft_cap, per_layer_sliding_window=per_layer_sliding_window, prefix=f'{i}.attn', attn_type=attn_type)\n    return attention_instances",
        "origin": "/tmp/vllm_repo/vllm/model_executor/models/transformers/base.py"
    },
    {
        "id": "is_supported_and_can_implement_kernel",
        "coords": [
            15,
            11,
            1
        ],
        "fiber": 27,
        "logic": "def is_supported_and_can_implement_kernel(kernel: type[_KernelT], config: _KernelConfigT, compute_capability: int | None) -> tuple[bool, str]:\n    if kernel.__name__ in envs.VLLM_DISABLED_KERNELS:\n        return (False, f' {kernel.__name__} is disabled by environment variable')\n    if compute_capability is None:\n        _cc = current_platform.get_device_capability()\n        if _cc is not None:\n            compute_capability = _cc[0] * 10 + _cc[1]\n    is_supported, failure_reason = kernel.is_supported(compute_capability)\n    if not is_supported:\n        return (False, f'{kernel.__name__} {failure_reason}.')\n    can_implement, failure_reason = kernel.can_implement(config)\n    if not can_implement:\n        return (False, f'{kernel.__name__} {failure_reason}.')\n    return (True, '')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/kernels/linear/__init__.py"
    },
    {
        "id": "choose_scaled_mm_linear_kernel",
        "coords": [
            17,
            25,
            3
        ],
        "fiber": 14,
        "logic": "def choose_scaled_mm_linear_kernel(config: _KernelConfigT, possible_kernels: dict[PlatformEnum, list[type[_KernelT]]], compute_capability: int | None=None, force_kernel: type[_KernelT] | None=None) -> type[_KernelT]:\n    \"\"\"\n    Choose a _KernelT that can implement the given config for the\n    given compute capability. Attempts to choose the best kernel in terms of\n    performance.\n\n    Args:\n        config (_KernelConfigT): Description of the linear layer\n            to be implemented.\n        possible_kernels (dict[PlatformEnum, list[_KernelT]]): A\n            dictionary of platforms and their list of possible kernels.\n        compute_capability (Optional[int], optional): The compute capability of\n            the target device, if None uses `current_platform` to get the\n            compute capability. Defaults to None.\n        force_kernel (Optional[type[_KernelT]]): An Optional forced kernel to override\n            the possible_kernels if it can be implemented. If None, it will only try the\n            possible kernels.\n\n    Raises:\n        ValueError: If no kernel can implement the given config.\n\n    Returns:\n        _KernelT: Chosen kernel.\n    \"\"\"\n    failure_reason_list = []\n    if force_kernel is not None:\n        can_implement, failure_reason = is_supported_and_can_implement_kernel(force_kernel, config, compute_capability)\n        if can_implement:\n            return force_kernel\n        logger.info_once(\"Tried to force %s, but the kernel couldn't be implemented\", force_kernel.__name__, scope='global')\n    for kernel in possible_kernels[current_platform._enum]:\n        is_supported_and_can_implement, failure_reason = is_supported_and_can_implement_kernel(kernel, config, compute_capability)\n        if is_supported_and_can_implement:\n            return kernel\n        failure_reason_list.append(failure_reason)\n    raise ValueError('Failed to find a kernel that can implement the ScaledMM linear layer. Reasons: \\n' + '\\n'.join(failure_reason_list))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/kernels/linear/__init__.py"
    },
    {
        "id": "init_fp8_linear_kernel",
        "coords": [
            21,
            0,
            17
        ],
        "fiber": 7,
        "logic": "def init_fp8_linear_kernel(activation_quant_key: QuantKey, weight_quant_key: QuantKey, out_dtype: torch.dtype, force_kernel: type[FP8ScaledMMLinearKernel] | None=None, module_name: str | None=None) -> FP8ScaledMMLinearKernel:\n    scaled_mm_linear_kernel_config = FP8ScaledMMLinearLayerConfig(weight_quant_key=weight_quant_key, activation_quant_key=activation_quant_key, out_dtype=out_dtype)\n    kernel_type = choose_scaled_mm_linear_kernel(scaled_mm_linear_kernel_config, _POSSIBLE_FP8_KERNELS, force_kernel=force_kernel)\n    if module_name:\n        logger.info_once('Selected %s for %s', kernel_type.__name__, module_name, scope='global')\n    return kernel_type(scaled_mm_linear_kernel_config, layer_param_names=['weight', 'weight_scale', 'input_scale', 'input_scale_ub'])",
        "origin": "/tmp/vllm_repo/vllm/model_executor/kernels/linear/__init__.py"
    },
    {
        "id": "init_int8_linear_kernel",
        "coords": [
            15,
            28,
            0
        ],
        "fiber": 12,
        "logic": "def init_int8_linear_kernel(is_channelwise: bool, is_static_input_scheme: bool, input_symmetric: bool, module_name: str) -> Int8ScaledMMLinearKernel:\n    config = Int8ScaledMMLinearLayerConfig(is_channelwise=is_channelwise, is_static_input_scheme=is_static_input_scheme, input_symmetric=input_symmetric)\n    kernel_type = choose_scaled_mm_linear_kernel(config, _POSSIBLE_INT8_KERNELS)\n    logger.info_once('Selected %s for %s', kernel_type.__name__, module_name, scope='global')\n    return kernel_type(config, layer_param_names=['weight', 'weight_scale', 'input_scale', 'input_zero_point', 'azp_adj'])",
        "origin": "/tmp/vllm_repo/vllm/model_executor/kernels/linear/__init__.py"
    },
    {
        "id": "choose_mp_linear_kernel",
        "coords": [
            24,
            1,
            5
        ],
        "fiber": 30,
        "logic": "def choose_mp_linear_kernel(config: MPLinearLayerConfig, compute_capability: int | None=None) -> type[MPLinearKernel]:\n    \"\"\"\n    Choose an MPLinearKernel that can implement the given config for the given\n     compute capability. Attempts to choose the best kernel in terms of\n     performance.\n\n    Args:\n        config (MPLinearLayerConfig): Description of the linear layer to be\n            implemented.\n        compute_capability (Optional[int], optional): The compute capability of\n            the target device, if None uses `current_platform` to get\n            the compute capability. Defaults to None.\n\n    Raises:\n        ValueError: If no kernel can implement the given config.\n\n    Returns:\n        type[MPLinearKernel]: Chosen kernel.\n    \"\"\"\n    if compute_capability is None:\n        if current_platform is None:\n            raise ValueError('Cannot determine compute capability')\n        _cc = current_platform.get_device_capability()\n        if _cc is not None:\n            compute_capability = _cc[0] * 10 + _cc[1]\n    failure_reasons = []\n    for kernel in _POSSIBLE_KERNELS[current_platform._enum]:\n        if kernel.__name__ in envs.VLLM_DISABLED_KERNELS:\n            failure_reasons.append(f' {kernel.__name__} disabled by environment variable')\n            continue\n        if compute_capability is not None and kernel.get_min_capability() > compute_capability:\n            failure_reasons.append(f'{kernel.__name__} requires capability {kernel.get_min_capability()}, current compute  capability is {compute_capability}')\n            continue\n        can_implement, failure_reason = kernel.can_implement(config)\n        if can_implement:\n            return kernel\n        else:\n            failure_reasons.append(f' {kernel.__name__} cannot implement due to: {failure_reason}')\n    raise ValueError('Failed to find a kernel that can implement the WNA16 linear layer. Reasons: \\n' + '\\n'.join(failure_reasons))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/kernels/linear/__init__.py"
    },
    {
        "id": "register_linear_kernel",
        "coords": [
            18,
            29,
            2
        ],
        "fiber": 18,
        "logic": "def register_linear_kernel(kernel_class: type, platform: PlatformEnum, kernel_type: str='mp') -> None:\n    \"\"\"\n    Register a new linear kernel class to be considered in kernel selection.\n\n    Args:\n        kernel_class (type): The kernel class to register.\n        platform (PlatformEnum): The platform for which this kernel is applicable.\n        kernel_type (str): The type of the kernel, either \"mp\", \"int8\", or \"fp8\".\n            Defaults to \"mp\".\n\n    Raises:\n        ValueError: If the kernel_type is not recognized.\n    \"\"\"\n    if kernel_type == 'mp':\n        if platform not in _POSSIBLE_KERNELS:\n            _POSSIBLE_KERNELS[platform] = []\n        _POSSIBLE_KERNELS[platform].append(kernel_class)\n    elif kernel_type == 'int8':\n        if platform not in _POSSIBLE_INT8_KERNELS:\n            _POSSIBLE_INT8_KERNELS[platform] = []\n        _POSSIBLE_INT8_KERNELS[platform].append(kernel_class)\n    elif kernel_type == 'fp8':\n        if platform not in _POSSIBLE_FP8_KERNELS:\n            _POSSIBLE_FP8_KERNELS[platform] = []\n        _POSSIBLE_FP8_KERNELS[platform].append(kernel_class)\n    else:\n        raise ValueError(f'Unrecognized kernel type: {kernel_type}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/kernels/linear/__init__.py"
    },
    {
        "id": "matmul_kernel_persistent",
        "coords": [
            12,
            30,
            11
        ],
        "fiber": 22,
        "logic": "@triton.jit(launch_metadata=_matmul_launch_metadata)\ndef matmul_kernel_persistent(a_ptr, b_ptr, c_ptr, bias_ptr, M, N, K, stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, GROUP_SIZE_M: tl.constexpr, NUM_SMS: tl.constexpr, A_LARGE: tl.constexpr, B_LARGE: tl.constexpr, C_LARGE: tl.constexpr, HAS_BIAS: tl.constexpr):\n    start_pid = tl.program_id(axis=0)\n    num_pid_m = tl.cdiv(M, BLOCK_SIZE_M)\n    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)\n    k_tiles = tl.cdiv(K, BLOCK_SIZE_K)\n    num_tiles = num_pid_m * num_pid_n\n    tile_id_c = start_pid - NUM_SMS\n    offs_k_for_mask = tl.arange(0, BLOCK_SIZE_K)\n    num_pid_in_group = GROUP_SIZE_M * num_pid_n\n    for tile_id in tl.range(start_pid, num_tiles, NUM_SMS, flatten=True):\n        pid_m, pid_n = _compute_pid(tile_id, num_pid_in_group, num_pid_m, GROUP_SIZE_M, NUM_SMS)\n        start_m = pid_m * BLOCK_SIZE_M\n        start_n = pid_n * BLOCK_SIZE_N\n        offs_am = start_m + tl.arange(0, BLOCK_SIZE_M)\n        offs_bn = start_n + tl.arange(0, BLOCK_SIZE_N)\n        if A_LARGE:\n            offs_am = offs_am.to(tl.int64)\n        if B_LARGE:\n            offs_bn = offs_bn.to(tl.int64)\n        offs_am = tl.where(offs_am < M, offs_am, 0)\n        offs_bn = tl.where(offs_bn < N, offs_bn, 0)\n        offs_am = tl.max_contiguous(tl.multiple_of(offs_am, BLOCK_SIZE_M), BLOCK_SIZE_M)\n        offs_bn = tl.max_contiguous(tl.multiple_of(offs_bn, BLOCK_SIZE_N), BLOCK_SIZE_N)\n        accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n        for ki in range(k_tiles):\n            if A_LARGE or B_LARGE:\n                offs_k = ki * BLOCK_SIZE_K + tl.arange(0, BLOCK_SIZE_K).to(tl.int64)\n            else:\n                offs_k = ki * BLOCK_SIZE_K + tl.arange(0, BLOCK_SIZE_K)\n            a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_k[None, :] * stride_ak)\n            b_ptrs = b_ptr + (offs_k[:, None] * stride_bk + offs_bn[None, :] * stride_bn)\n            a = tl.load(a_ptrs, mask=offs_k_for_mask[None, :] < K - ki * BLOCK_SIZE_K, other=0.0)\n            b = tl.load(b_ptrs, mask=offs_k_for_mask[:, None] < K - ki * BLOCK_SIZE_K, other=0.0)\n            accumulator = tl.dot(a, b, accumulator)\n        tile_id_c += NUM_SMS\n        pid_m, pid_n = _compute_pid(tile_id_c, num_pid_in_group, num_pid_m, GROUP_SIZE_M, NUM_SMS)\n        offs_cm = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n        offs_cn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n        if C_LARGE:\n            offs_cm = offs_cm.to(tl.int64)\n            offs_cn = offs_cn.to(tl.int64)\n        c_ptrs = c_ptr + stride_cm * offs_cm[:, None] + stride_cn * offs_cn[None, :]\n        c_mask = (offs_cm[:, None] < M) & (offs_cn[None, :] < N)\n        if HAS_BIAS:\n            bias_ptrs = bias_ptr + offs_cn\n            bias = tl.load(bias_ptrs, mask=offs_cn < N, other=0.0).to(tl.float32)\n            accumulator += bias\n        c = accumulator.to(c_ptr.dtype.element_ty)\n        tl.store(c_ptrs, c, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/batch_invariant.py"
    },
    {
        "id": "bmm_kernel",
        "coords": [
            8,
            9,
            19
        ],
        "fiber": 5,
        "logic": "@triton.jit\ndef bmm_kernel(a_ptr, b_ptr, c_ptr, B, M, N, K, stride_ab, stride_am, stride_ak, stride_bb, stride_bk, stride_bn, stride_cb, stride_cm, stride_cn, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, A_LARGE: tl.constexpr, B_LARGE: tl.constexpr, C_LARGE: tl.constexpr):\n    \"\"\"Batched GEMM: (B, M, K) x (B, K, N) -> (B, M, N)\n\n    Each program computes one (batch_idx, tile_m, tile_n) tile, accumulating\n    along K in a fixed order to preserve batch invariance.\n    \"\"\"\n    pid_b = tl.program_id(0)\n    pid = tl.program_id(1)\n    if pid_b >= B:\n        return\n    num_pid_m = tl.cdiv(M, BLOCK_SIZE_M)\n    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)\n    pid_m = pid // num_pid_n\n    pid_n = pid % num_pid_n\n    if pid_m >= num_pid_m or pid_n >= num_pid_n:\n        return\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    mask_m = offs_m < M\n    mask_n = offs_n < N\n    if A_LARGE or B_LARGE or C_LARGE:\n        offs_m = offs_m.to(tl.int64)\n        offs_n = offs_n.to(tl.int64)\n    offs_m = tl.where(mask_m, offs_m, 0)\n    offs_n = tl.where(mask_n, offs_n, 0)\n    offs_m = tl.max_contiguous(tl.multiple_of(offs_m, BLOCK_SIZE_M), BLOCK_SIZE_M)\n    offs_n = tl.max_contiguous(tl.multiple_of(offs_n, BLOCK_SIZE_N), BLOCK_SIZE_N)\n    a_batch_ptr = a_ptr + pid_b * stride_ab\n    b_batch_ptr = b_ptr + pid_b * stride_bb\n    c_batch_ptr = c_ptr + pid_b * stride_cb\n    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n    k_tiles = tl.cdiv(K, BLOCK_SIZE_K)\n    offs_k_mask = tl.arange(0, BLOCK_SIZE_K)\n    for ki in range(k_tiles):\n        if A_LARGE or B_LARGE:\n            offs_k = ki * BLOCK_SIZE_K + tl.arange(0, BLOCK_SIZE_K).to(tl.int64)\n        else:\n            offs_k = ki * BLOCK_SIZE_K + tl.arange(0, BLOCK_SIZE_K)\n        a_ptrs = a_batch_ptr + (offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak)\n        b_ptrs = b_batch_ptr + (offs_k[:, None] * stride_bk + offs_n[None, :] * stride_bn)\n        k_valid = offs_k_mask < K - ki * BLOCK_SIZE_K\n        a_mask = mask_m[:, None] & k_valid[None, :]\n        b_mask = k_valid[:, None] & mask_n[None, :]\n        a = tl.load(a_ptrs, mask=a_mask, other=0.0)\n        b = tl.load(b_ptrs, mask=b_mask, other=0.0)\n        accumulator = tl.dot(a, b, accumulator)\n    c_m = offs_m\n    c_n = offs_n\n    if C_LARGE:\n        c_m = c_m.to(tl.int64)\n        c_n = c_n.to(tl.int64)\n    c_ptrs = c_batch_ptr + stride_cm * c_m[:, None] + stride_cn * c_n[None, :]\n    c_mask = mask_m[:, None] & mask_n[None, :]\n    c = accumulator.to(c_ptr.dtype.element_ty)\n    tl.store(c_ptrs, c, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/batch_invariant.py"
    },
    {
        "id": "_log_softmax_kernel",
        "coords": [
            15,
            28,
            21
        ],
        "fiber": 2,
        "logic": "@triton.jit\ndef _log_softmax_kernel(input_ptr, output_ptr, input_row_stride, output_row_stride, n_cols, BLOCK_SIZE: tl.constexpr):\n    \"\"\"\n    Compute log_softmax along the last dimension of a 2D tensor.\n    Each block handles one row of the input tensor.\n    \"\"\"\n    row_idx = tl.program_id(0).to(tl.int64)\n    row_start_ptr = input_ptr + row_idx * input_row_stride\n    output_row_start_ptr = output_ptr + row_idx * output_row_stride\n    max_val = -float('inf')\n    for col_offset in range(0, n_cols, BLOCK_SIZE):\n        col_idx = col_offset + tl.arange(0, BLOCK_SIZE)\n        mask = col_idx < n_cols\n        vals = tl.load(row_start_ptr + col_idx, mask=mask, other=-float('inf'))\n        max_val = tl.max(tl.maximum(vals, max_val))\n    sum_exp = 0.0\n    for col_offset in range(0, n_cols, BLOCK_SIZE):\n        col_idx = col_offset + tl.arange(0, BLOCK_SIZE)\n        mask = col_idx < n_cols\n        vals = tl.load(row_start_ptr + col_idx, mask=mask, other=0.0)\n        exp_vals = tl.exp(vals - max_val)\n        sum_exp += tl.sum(tl.where(mask, exp_vals, 0.0))\n    log_sum_exp = tl.log(sum_exp)\n    for col_offset in range(0, n_cols, BLOCK_SIZE):\n        col_idx = col_offset + tl.arange(0, BLOCK_SIZE)\n        mask = col_idx < n_cols\n        vals = tl.load(row_start_ptr + col_idx, mask=mask)\n        output = vals - max_val - log_sum_exp\n        tl.store(output_row_start_ptr + col_idx, output, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/batch_invariant.py"
    },
    {
        "id": "mean_kernel",
        "coords": [
            30,
            22,
            1
        ],
        "fiber": 22,
        "logic": "@triton.jit\ndef mean_kernel(input_ptr, output_ptr, input_stride0, input_stride1, input_stride2, output_stride0, output_stride1, M, N, K, BLOCK_SIZE: tl.constexpr):\n    \"\"\"\n    Kernel for computing mean along a single dimension.\n    Input is viewed as (M, N, K) where N is the dimension being reduced.\n    \"\"\"\n    pid = tl.program_id(0)\n    m_idx = pid // K\n    k_idx = pid % K\n    if m_idx >= M or k_idx >= K:\n        return\n    acc = 0.0\n    for n_start in range(0, N, BLOCK_SIZE):\n        n_offsets = n_start + tl.arange(0, BLOCK_SIZE)\n        mask = n_offsets < N\n        input_idx = m_idx * input_stride0 + n_offsets * input_stride1 + k_idx * input_stride2\n        vals = tl.load(input_ptr + input_idx, mask=mask, other=0.0)\n        acc += tl.sum(vals)\n    mean_val = acc / N\n    output_idx = m_idx * output_stride0 + k_idx * output_stride1\n    tl.store(output_ptr + output_idx, mean_val)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/batch_invariant.py"
    },
    {
        "id": "_rms_norm_kernel",
        "coords": [
            13,
            16,
            19
        ],
        "fiber": 17,
        "logic": "@triton.jit\ndef _rms_norm_kernel(input_ptr, weight_ptr, output_ptr, input_row_stride, output_row_stride, n_cols, eps, BLOCK_SIZE: tl.constexpr):\n    \"\"\"\n    Compute RMS normalization along the last dimension of a 2D tensor.\n    RMS Norm: y = x / sqrt(mean(x^2) + eps) * weight\n    Each block handles one row of the input tensor.\n    \"\"\"\n    row_idx = tl.program_id(0).to(tl.int64)\n    row_start_ptr = input_ptr + row_idx * input_row_stride\n    output_row_start_ptr = output_ptr + row_idx * output_row_stride\n    sum_sq = tl.zeros([1], dtype=tl.float32)\n    for col_offset in range(0, n_cols, BLOCK_SIZE):\n        col_idx = col_offset + tl.arange(0, BLOCK_SIZE)\n        mask = col_idx < n_cols\n        vals = tl.load(row_start_ptr + col_idx, mask=mask, other=0.0)\n        vals_f32 = vals.to(tl.float32)\n        sq_vals = vals_f32 * vals_f32\n        sum_sq += tl.sum(tl.where(mask, sq_vals, 0.0))\n    mean_sq = sum_sq / n_cols\n    rms = tl.sqrt(mean_sq + eps)\n    inv_rms = 1.0 / rms\n    for col_offset in range(0, n_cols, BLOCK_SIZE):\n        col_idx = col_offset + tl.arange(0, BLOCK_SIZE)\n        mask = col_idx < n_cols\n        vals = tl.load(row_start_ptr + col_idx, mask=mask, other=0.0)\n        weight = tl.load(weight_ptr + col_idx, mask=mask, other=1.0)\n        vals_f32 = vals.to(tl.float32)\n        weight_f32 = weight.to(tl.float32)\n        output_f32 = vals_f32 * inv_rms * weight_f32\n        output = output_f32.to(vals.dtype)\n        tl.store(output_row_start_ptr + col_idx, output, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/batch_invariant.py"
    },
    {
        "id": "kda_attention",
        "coords": [
            0,
            9,
            22
        ],
        "fiber": 0,
        "logic": "def kda_attention(q_proj_states: torch.Tensor, k_proj_states: torch.Tensor, v_proj_states: torch.Tensor, g1: torch.Tensor, beta: torch.Tensor, core_attn_out: torch.Tensor, layer_name: str) -> None:\n    forward_context: ForwardContext = get_forward_context()\n    self = forward_context.no_compile_layers[layer_name]\n    self._forward(q_proj_states=q_proj_states, k_proj_states=k_proj_states, v_proj_states=v_proj_states, g1=g1, beta=beta, core_attn_out=core_attn_out)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/kda.py"
    },
    {
        "id": "kda_attention_fake",
        "coords": [
            21,
            1,
            19
        ],
        "fiber": 10,
        "logic": "def kda_attention_fake(q_proj_states: torch.Tensor, k_proj_states: torch.Tensor, v_proj_states: torch.Tensor, g1: torch.Tensor, beta: torch.Tensor, core_attn_out: torch.Tensor, layer_name: str) -> None:\n    return",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/kda.py"
    },
    {
        "id": "check_cpu_sgl_kernel",
        "coords": [
            13,
            2,
            0
        ],
        "fiber": 15,
        "logic": "def check_cpu_sgl_kernel(n: int, k: int, dtype: torch.dtype) -> bool:\n    return torch.cpu._is_amx_tile_supported() and dtype in (torch.bfloat16, torch.int8) and (k % 32 == 0) and (n % 16 == 0)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/utils.py"
    },
    {
        "id": "_fwd_diag_kernel",
        "coords": [
            20,
            22,
            25
        ],
        "fiber": 5,
        "logic": "@triton.jit\ndef _fwd_diag_kernel(Q, K, V, Out, S, b: tl.constexpr, h: tl.constexpr, n, d: tl.constexpr, e: tl.constexpr, BLOCK: tl.constexpr, NUM_BLOCK, CBLOCK: tl.constexpr):\n    off = tl.program_id(0)\n    off_bh = off // NUM_BLOCK\n    off_block = off % NUM_BLOCK\n    off_cblock = tl.program_id(1)\n    off_h = off_bh % h\n    qk_offset = off_bh * n * d\n    v_offset = off_bh * n * e\n    o_offset = off_bh * n * e\n    block_offset = off_block * BLOCK\n    qk_block_offset = block_offset * d\n    v_block_offset = block_offset * e\n    o_block_offset = block_offset * e\n    cblock_offset = off_cblock * CBLOCK\n    q_cblock_offset = cblock_offset * d\n    o_cblock_offset = cblock_offset * e\n    Q_block_ptr = Q + qk_offset + qk_block_offset + q_cblock_offset + tl.arange(0, CBLOCK)[:, None] * d + tl.arange(0, d)[None, :]\n    K_trans_block_ptr = K + qk_offset + qk_block_offset + tl.arange(0, CBLOCK)[None, :] * d + tl.arange(0, d)[:, None]\n    V_block_ptr = V + v_offset + v_block_offset + tl.arange(0, CBLOCK)[:, None] * e + tl.arange(0, e)[None, :]\n    O_block_ptr = Out + o_offset + o_block_offset + o_cblock_offset + tl.arange(0, CBLOCK)[:, None] * e + tl.arange(0, e)[None, :]\n    S_block_ptr = S + off_h\n    s = tl.load(S_block_ptr)\n    i = off_cblock\n    q_index = tl.arange(0, CBLOCK) + i * CBLOCK\n    q = tl.load(Q_block_ptr, mask=block_offset + q_index[:, None] < n, other=0.0).to(tl.float32)\n    qkv = tl.zeros([CBLOCK, e], dtype=tl.float32)\n    for j in range(i + 1):\n        kv_index = tl.arange(0, CBLOCK) + j * CBLOCK\n        diff = q_index[:, None] - kv_index[None, :]\n        s_index = s * diff\n        s_index = tl.where(diff >= 0, -s_index, float('-inf'))\n        decay = tl.exp(s_index)\n        k_trans = tl.load(K_trans_block_ptr, mask=block_offset + kv_index[None, :] < n, other=0.0).to(tl.float32)\n        v = tl.load(V_block_ptr, mask=block_offset + kv_index[:, None] < n, other=0.0).to(tl.float32)\n        qk = tl.dot(q, k_trans) * decay\n        qkv += tl.dot(qk, v)\n        K_trans_block_ptr += CBLOCK * d\n        V_block_ptr += CBLOCK * e\n    tl.store(O_block_ptr, qkv.to(O_block_ptr.dtype.element_ty), mask=block_offset + q_index[:, None] < n)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/lightning_attn.py"
    },
    {
        "id": "_fwd_none_diag_kernel",
        "coords": [
            16,
            2,
            19
        ],
        "fiber": 6,
        "logic": "@triton.jit\ndef _fwd_none_diag_kernel(Q, Out, S, KV, b: tl.constexpr, h: tl.constexpr, n, d: tl.constexpr, e: tl.constexpr, BLOCK: tl.constexpr, NUM_BLOCK, E_FBLOCK: tl.constexpr, CBLOCK: tl.constexpr, NUM_CBLOCK: tl.constexpr):\n    off_bh = tl.program_id(0)\n    off_h = off_bh % h\n    off_nc = tl.program_id(1)\n    off_n = off_nc // NUM_CBLOCK\n    off_c = off_nc % NUM_CBLOCK\n    off_e = tl.program_id(2)\n    n_offset = off_n * BLOCK\n    c_offset = off_c * CBLOCK\n    e_offset = off_e * E_FBLOCK\n    block_offset = n_offset + c_offset\n    q_offset = off_bh * n * d + (n_offset + c_offset) * d\n    o_offset = off_bh * n * e + (n_offset + c_offset) * e + e_offset\n    kv_offset = off_bh * NUM_BLOCK * d * e + off_n * d * e + e_offset\n    Q_block_ptr = Q + q_offset + tl.arange(0, CBLOCK)[:, None] * d + tl.arange(0, d)[None, :]\n    O_block_ptr = Out + o_offset + tl.arange(0, CBLOCK)[:, None] * e + tl.arange(0, E_FBLOCK)[None, :]\n    KV_block_ptr = KV + kv_offset + tl.arange(0, d)[:, None] * e + tl.arange(0, E_FBLOCK)[None, :]\n    S_block_ptr = S + off_h\n    s = tl.load(S_block_ptr)\n    c_array = tl.arange(0, CBLOCK)\n    kv = tl.load(KV_block_ptr).to(tl.float32)\n    q_index = block_offset + tl.arange(0, CBLOCK)\n    q = tl.load(Q_block_ptr, mask=q_index[:, None] < n, other=0.0).to(tl.float32)\n    q_decay = tl.exp(-s.to(tl.float32) * (off_c * CBLOCK + c_array[:, None]))\n    qkv_none_diag = tl.dot(q, kv) * q_decay\n    qkv_diag = tl.load(O_block_ptr, mask=q_index[:, None] < n, other=0.0).to(tl.float32)\n    qkv = qkv_diag + qkv_none_diag\n    tl.store(O_block_ptr, qkv.to(O_block_ptr.dtype.element_ty), mask=q_index[:, None] < n)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/lightning_attn.py"
    },
    {
        "id": "lightning_attention",
        "coords": [
            27,
            28,
            24
        ],
        "fiber": 17,
        "logic": "def lightning_attention(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, ed: torch.Tensor, block_size: int=256, kv_history: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor]:\n    \"\"\"\n    Apply lightning attention algorithm\n    to compute attention efficiently.\n\n    Args:\n        q: Query tensor of shape [batch, heads, seq_len, dim]\n        k: Key tensor of shape [batch, heads, seq_len, dim]\n        v: Value tensor of shape [batch, heads, seq_len, dim_v]\n        ed: Decay rate tensor of shape [heads]\n        block_size: Size of blocks for block-sparse attention\n        kv_history: Optional key-value history from previous computations\n\n    Returns:\n        output: Attention output\n        kv: Updated key-value history\n    \"\"\"\n    d = q.shape[-1]\n    e = v.shape[-1]\n    if ed.dim() == 1:\n        ed = ed.view(1, -1, 1, 1)\n    m = 128 if d >= 128 else 64\n    assert d % m == 0, f'Dimension d ({d}) must be divisible by m ({m})'\n    arr = [m * i for i in range(d // m + 1)]\n    if arr[-1] != d:\n        arr.append(d)\n    n = len(arr)\n    output = 0\n    if kv_history is None:\n        kv_history = torch.zeros((q.shape[0], q.shape[1], d, e), dtype=torch.float32, device=q.device)\n    else:\n        kv_history = kv_history.clone().contiguous()\n    for i in range(n - 1):\n        s = arr[i]\n        e = arr[i + 1]\n        q1 = q[..., s:e]\n        k1 = k[..., s:e]\n        o, kv = lightning_attention_(q1, k1, v, ed, kv_history)\n        output = output + o\n    return (output, kv)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/lightning_attn.py"
    },
    {
        "id": "_linear_attn_decode_kernel",
        "coords": [
            22,
            6,
            18
        ],
        "fiber": 15,
        "logic": "@triton.jit\ndef _linear_attn_decode_kernel(q_ptr, k_ptr, v_ptr, kv_cache_ptr, slope_rate, slot_idx, output_ptr, D: tl.constexpr, qkv_b_stride, qkv_h_stride, cache_b_stride, cache_h_stride, cache_d0_stride, cache_d1_stride, pad_slot_id: tl.constexpr, BLOCK_SIZE: tl.constexpr):\n    \"\"\"\n    Kernel for linear attention decoding with KV cache.\n\n    This kernel computes attention for a single token using the KV cache.\n    \"\"\"\n    pid_b = tl.program_id(0)\n    pid_h = tl.program_id(1)\n    pid_d = tl.program_id(2)\n    slot_id = tl.load(slot_idx + pid_b).to(tl.int64)\n    if slot_id == pad_slot_id:\n        return\n    batch_id = pid_b\n    head_id = pid_h\n    ratio = tl.load(slope_rate + pid_h)\n    qk_d_offsets = tl.arange(0, D)\n    v_d_offsets = tl.arange(0, BLOCK_SIZE) + pid_d * BLOCK_SIZE\n    cache_d_offsets = qk_d_offsets[:, None] * cache_d0_stride + v_d_offsets[None, :] * cache_d1_stride\n    q_offset = batch_id * qkv_b_stride + head_id * qkv_h_stride\n    k_offset = batch_id * qkv_b_stride + head_id * qkv_h_stride\n    v_offset = batch_id * qkv_b_stride + head_id * qkv_h_stride\n    cache_offset = slot_id * cache_b_stride + head_id * cache_h_stride\n    qk_mask = qk_d_offsets < D\n    v_mask = v_d_offsets < D\n    q = tl.load(q_ptr + q_offset + qk_d_offsets, mask=qk_mask, other=0.0)\n    k = tl.load(k_ptr + k_offset + qk_d_offsets, mask=qk_mask, other=0.0)\n    v = tl.load(v_ptr + v_offset + v_d_offsets, mask=v_mask, other=0.0)\n    kv_outer = k[:, None] * v[None, :]\n    kv_mask = qk_mask[:, None] & v_mask[None, :]\n    ratio = tl.exp(-ratio)\n    kv_ptr = kv_cache_ptr + cache_offset + cache_d_offsets\n    kv_cache_old = tl.load(kv_ptr, mask=kv_mask, other=0.0)\n    kv_outer = kv_outer + ratio * kv_cache_old\n    output = q[:, None].to(tl.float32) * kv_outer\n    output = tl.sum(output, axis=0)\n    tl.store(kv_ptr, kv_outer, mask=kv_mask)\n    tl.store(output_ptr + q_offset + v_d_offsets, output, mask=v_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/lightning_attn.py"
    },
    {
        "id": "_swiglustep_and_mul_kernel",
        "coords": [
            7,
            26,
            13
        ],
        "fiber": 15,
        "logic": "@triton.jit\ndef _swiglustep_and_mul_kernel(o_ptr, o_stride, x_ptr, x_stride, limit: tl.constexpr, d: tl.constexpr, BLOCK_SIZE: tl.constexpr) -> None:\n    i = tl.program_id(axis=0).to(tl.int64)\n    j = tl.program_id(axis=1)\n    o_row_ptr = o_ptr + o_stride * i\n    x_row_ptr = x_ptr + x_stride * i\n    offsets = j * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)\n    mask = offsets < d\n    gate = tl.load(x_row_ptr + offsets, mask=mask).to(tl.float32)\n    up = tl.load(x_row_ptr + offsets + d, mask=mask).to(tl.float32)\n    gate_silu = tl.sigmoid(gate) * gate\n    gate_clamped = tl.minimum(gate_silu, limit)\n    up_clamped = tl.minimum(tl.maximum(up, -limit), limit)\n    result = gate_clamped * up_clamped\n    result = result.to(x_ptr.dtype.element_ty)\n    tl.store(o_row_ptr + offsets, result, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/activation.py"
    },
    {
        "id": "create_static_sink_attention_backend",
        "coords": [
            14,
            13,
            30
        ],
        "fiber": 26,
        "logic": "@functools.lru_cache\ndef create_static_sink_attention_backend(underlying_attn_backend: type[AttentionBackend], sink_len: int=0) -> type[AttentionBackend]:\n    prefix = 'StaticSink_'\n    underlying_builder = underlying_attn_backend.get_builder_cls()\n\n    class StaticSinkAttentionBuilder(underlying_builder):\n\n        def __init__(self, kv_cache_spec: AttentionSpec, layer_names: list[str], vllm_config: VllmConfig, device: torch.device):\n            super().__init__(kv_cache_spec, layer_names, vllm_config, device)\n            model_config = vllm_config.model_config\n            scheduler_config = vllm_config.scheduler_config\n            self.sink_len = sink_len\n            self.block_size = vllm_config.cache_config.block_size\n            self.num_sink_blocks = self.sink_len // vllm_config.cache_config.block_size\n            self.max_num_blocks = cdiv(model_config.max_model_len, vllm_config.cache_config.block_size)\n            self.block_table_with_sink = torch.zeros((scheduler_config.max_num_seqs, self.max_num_blocks + self.num_sink_blocks), device=device, dtype=torch.int32)\n            self.block_table_with_sink[:, :self.num_sink_blocks] = torch.arange(1, self.num_sink_blocks + 1, device=device, dtype=torch.int32)\n\n        def build(self, common_prefix_len: int, common_attn_metadata: CommonAttentionMetadata, fast_build: bool=False) -> AttentionMetadata:\n            common_attn_metadata.seq_lens[:] = common_attn_metadata.seq_lens + self.sink_len\n            common_attn_metadata.seq_lens[common_attn_metadata.seq_lens == self.sink_len] = 0\n            common_attn_metadata.max_seq_len = common_attn_metadata.max_seq_len + self.sink_len\n            max_num_blocks = cdiv(common_attn_metadata.max_seq_len, self.block_size)\n            num_reqs = common_attn_metadata.num_reqs\n            self.block_table_with_sink[:num_reqs, self.num_sink_blocks:self.num_sink_blocks + max_num_blocks] = common_attn_metadata.block_table_tensor[:, :max_num_blocks]\n            common_attn_metadata.block_table_tensor = self.block_table_with_sink[:num_reqs]\n            return super().build(common_prefix_len, common_attn_metadata, fast_build)\n    attn_backend = subclass_attention_backend(name_prefix=prefix, attention_backend_cls=underlying_attn_backend, builder_cls=StaticSinkAttentionBuilder)\n    return attn_backend",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/static_sink_attention.py"
    },
    {
        "id": "create_chunked_local_attention_backend",
        "coords": [
            15,
            27,
            8
        ],
        "fiber": 19,
        "logic": "@functools.lru_cache\ndef create_chunked_local_attention_backend(underlying_attn_backend: AttentionBackend, attention_chunk_size: int) -> type[AttentionBackend]:\n    prefix = f'ChunkedLocalAttention_{attention_chunk_size}_'\n    underlying_builder = underlying_attn_backend.get_builder_cls()\n    assert issubclass(underlying_builder, AttentionMetadataBuilder)\n\n    class ChunkedLocalAttentionBuilder(underlying_builder):\n\n        @classmethod\n        def get_cudagraph_support(cls: type['AttentionMetadataBuilder'], vllm_config: VllmConfig, kv_cache_spec: AttentionSpec) -> AttentionCGSupport:\n            return AttentionCGSupport.NEVER\n\n        def build(self, common_prefix_len: int, common_attn_metadata: CommonAttentionMetadata, fast_build: bool=False):\n            cm, make_virtual_batches_block_table = make_local_attention_virtual_batches(attention_chunk_size, common_attn_metadata, self.kv_cache_spec.block_size)\n            metadata = super().build(common_prefix_len, cm, fast_build)\n            metadata.make_virtual_batches_block_table = make_virtual_batches_block_table\n            return metadata\n\n        def update_block_table(self, metadata, blk_table: torch.Tensor, slot_mapping: torch.Tensor):\n            blk_table = metadata.make_virtual_batches_block_table(blk_table)\n            return super().update_block_table(metadata, blk_table, slot_mapping)\n    attn_backend = subclass_attention_backend(name_prefix=prefix, attention_backend_cls=underlying_attn_backend, builder_cls=ChunkedLocalAttentionBuilder)\n    return attn_backend",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/chunked_local_attention.py"
    },
    {
        "id": "get_attention_context",
        "coords": [
            25,
            13,
            27
        ],
        "fiber": 3,
        "logic": "def get_attention_context(layer_name: str) -> tuple[Any, 'Attention | MLAAttention', torch.Tensor, torch.Tensor]:\n    \"\"\"Extract attention context for a given layer.\n\n    This helper function extracts the attention metadata, attention layer\n    instance, KV cache tensor, and slot mapping for a specific layer.\n\n    Args:\n        layer_name: The name/identifier of the attention layer.\n\n    Returns:\n        A tuple containing:\n        - attn_metadata: Attention metadata for this specific layer, or None if\n            no metadata available\n        - attn_layer: The attention layer instance (Attention or MLAAttention)\n        - kv_cache: The KV cache tensor for current forward pass\n        - slot_mapping: The slot mapping for this specific layer\n\n        Note: attn_metadata may be None, but attn_layer and kv_cache are always\n        extracted from the forward context.\n    \"\"\"\n    forward_context: ForwardContext = get_forward_context()\n    attn_metadata = forward_context.attn_metadata\n    if isinstance(attn_metadata, dict):\n        attn_metadata = attn_metadata[layer_name]\n    attn_layer: Attention | MLAAttention = forward_context.no_compile_layers[layer_name]\n    kv_cache = attn_layer.kv_cache\n    slot_mapping = forward_context.slot_mapping\n    assert isinstance(slot_mapping, dict), f'Expected slot_mapping to be a dict, got {type(slot_mapping)}. '\n    layer_slot_mapping = slot_mapping.get(layer_name)\n    return (attn_metadata, attn_layer, kv_cache, layer_slot_mapping)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/attention.py"
    },
    {
        "id": "unified_attention",
        "coords": [
            3,
            22,
            16
        ],
        "fiber": 10,
        "logic": "@maybe_transfer_kv_layer\ndef unified_attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, layer_name: str) -> torch.Tensor:\n    attn_metadata, self, kv_cache, _ = get_attention_context(layer_name)\n    output = self.impl.forward(self, query, key, value, kv_cache, attn_metadata)\n    return output",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/attention.py"
    },
    {
        "id": "unified_attention_fake",
        "coords": [
            20,
            19,
            15
        ],
        "fiber": 23,
        "logic": "def unified_attention_fake(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, layer_name: str) -> torch.Tensor:\n    return torch.empty_like(query).contiguous()",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/attention.py"
    },
    {
        "id": "unified_attention_with_output",
        "coords": [
            5,
            24,
            18
        ],
        "fiber": 16,
        "logic": "@maybe_transfer_kv_layer\ndef unified_attention_with_output(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, output: torch.Tensor, layer_name: str, output_scale: torch.Tensor | None=None, output_block_scale: torch.Tensor | None=None, kv_cache_dummy_dep: torch.Tensor | None=None) -> None:\n    del kv_cache_dummy_dep\n    attn_metadata, self, kv_cache, _ = get_attention_context(layer_name)\n    self.impl.forward(self, query, key, value, kv_cache, attn_metadata, output=output, output_scale=output_scale, output_block_scale=output_block_scale)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/attention.py"
    },
    {
        "id": "unified_attention_with_output_fake",
        "coords": [
            12,
            27,
            0
        ],
        "fiber": 8,
        "logic": "def unified_attention_with_output_fake(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, output: torch.Tensor, layer_name: str, output_scale: torch.Tensor | None=None, output_block_scale: torch.Tensor | None=None, kv_cache_dummy_dep: torch.Tensor | None=None) -> None:\n    return",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/attention.py"
    },
    {
        "id": "unified_mla_attention",
        "coords": [
            21,
            5,
            28
        ],
        "fiber": 23,
        "logic": "@maybe_transfer_kv_layer\ndef unified_mla_attention(q: torch.Tensor, kv_c_normed: torch.Tensor, k_pe: torch.Tensor, layer_name: str, kv_cache_dummy_dep: torch.Tensor | None=None) -> torch.Tensor:\n    del kv_cache_dummy_dep\n    attn_metadata, layer, kv_cache, _ = get_attention_context(layer_name)\n    output = layer.forward_impl(q, kv_c_normed, k_pe, kv_cache, attn_metadata)\n    return output",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/mla_attention.py"
    },
    {
        "id": "unified_mla_attention_fake",
        "coords": [
            15,
            20,
            11
        ],
        "fiber": 15,
        "logic": "def unified_mla_attention_fake(q: torch.Tensor, kv_c_normed: torch.Tensor, k_pe: torch.Tensor, layer_name: str, kv_cache_dummy_dep: torch.Tensor | None=None) -> torch.Tensor:\n    return torch.empty_like(q).contiguous()",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/mla_attention.py"
    },
    {
        "id": "unified_mla_attention_with_output",
        "coords": [
            27,
            3,
            25
        ],
        "fiber": 24,
        "logic": "@maybe_transfer_kv_layer\ndef unified_mla_attention_with_output(q: torch.Tensor, kv_c_normed: torch.Tensor, k_pe: torch.Tensor, output: torch.Tensor, layer_name: str, output_scale: torch.Tensor | None=None, output_block_scale: torch.Tensor | None=None, kv_cache_dummy_dep: torch.Tensor | None=None) -> None:\n    del kv_cache_dummy_dep\n    attn_metadata, layer, kv_cache, _ = get_attention_context(layer_name)\n    layer.forward_impl(q, kv_c_normed, k_pe, kv_cache, attn_metadata, output=output, output_scale=output_scale, output_block_scale=output_block_scale)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/mla_attention.py"
    },
    {
        "id": "unified_mla_attention_with_output_fake",
        "coords": [
            16,
            17,
            13
        ],
        "fiber": 15,
        "logic": "def unified_mla_attention_with_output_fake(q: torch.Tensor, kv_c_normed: torch.Tensor, k_pe: torch.Tensor, output: torch.Tensor, layer_name: str, output_scale: torch.Tensor | None=None, output_block_scale: torch.Tensor | None=None, kv_cache_dummy_dep: torch.Tensor | None=None) -> None:\n    return",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/mla_attention.py"
    },
    {
        "id": "create_encoder_only_attention_backend",
        "coords": [
            14,
            27,
            26
        ],
        "fiber": 5,
        "logic": "@functools.lru_cache\ndef create_encoder_only_attention_backend(underlying_attn_backend: AttentionBackend) -> type[AttentionBackend]:\n    prefix = 'EncoderOnlyAttention_'\n    underlying_builder = underlying_attn_backend.get_builder_cls()\n\n    class EncoderOnlyAttentionBuilder(underlying_builder):\n\n        def build(self, common_prefix_len: int, common_attn_metadata: CommonAttentionMetadata, fast_build: bool=False) -> AttentionMetadata:\n            new_common_attn_metadata = copy(common_attn_metadata)\n            new_common_attn_metadata.causal = False\n            return super().build(common_prefix_len, new_common_attn_metadata, fast_build)\n    attn_backend = subclass_attention_backend(name_prefix=prefix, attention_backend_cls=underlying_attn_backend, builder_cls=EncoderOnlyAttentionBuilder)\n    return attn_backend",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/encoder_only_attention.py"
    },
    {
        "id": "create_cross_attention_backend",
        "coords": [
            16,
            27,
            16
        ],
        "fiber": 28,
        "logic": "@functools.lru_cache\ndef create_cross_attention_backend(underlying_attn_backend: AttentionBackend) -> type[AttentionBackend]:\n    prefix = 'CrossAttention_'\n    underlying_builder = underlying_attn_backend.get_builder_cls()\n    underlying_impl = underlying_attn_backend.get_impl_cls()\n\n    class CrossAttentionBuilder(underlying_builder):\n\n        def build(self, common_prefix_len: int, common_attn_metadata: CommonAttentionMetadata, fast_build: bool=False) -> AttentionMetadata:\n            new_metadata = copy(common_attn_metadata)\n            new_metadata.causal = False\n            max_encoder_len = int(new_metadata.encoder_seq_lens_cpu.max())\n            new_metadata.max_seq_len = max_encoder_len\n            num_cache_decodes = (common_attn_metadata.num_computed_tokens_cpu > 0).sum().item()\n            if num_cache_decodes > 0:\n                num_tokens = common_attn_metadata.num_computed_tokens_cpu.numpy()\n                new_metadata.encoder_seq_lens_cpu = np.where(num_tokens > 0, 0, new_metadata.encoder_seq_lens_cpu)\n            new_metadata.seq_lens = common_attn_metadata.encoder_seq_lens\n            new_metadata._seq_lens_cpu = torch.from_numpy(common_attn_metadata.encoder_seq_lens_cpu)\n            slot_mapping = _get_cross_slot_mapping(new_metadata.encoder_seq_lens_cpu, new_metadata.block_table_tensor, self.kv_cache_spec, self.device)\n            attn_metadata = super().build(common_prefix_len, new_metadata, fast_build)\n            attn_metadata.slot_mapping = slot_mapping\n            return attn_metadata\n\n    class CrossAttentionImpl(underlying_impl):\n\n        def forward(self, layer: torch.nn.Module, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, kv_cache: torch.Tensor, attn_metadata: AttentionMetadata, output: torch.Tensor | None=None, output_scale: torch.Tensor | None=None, output_block_scale: torch.Tensor | None=None) -> torch.Tensor:\n            if not underlying_attn_backend.forward_includes_kv_cache_update and attn_metadata is not None and (layer.kv_sharing_target_layer_name is None) and (key is not None) and (value is not None):\n                self.do_kv_cache_update(layer, key, value, kv_cache, attn_metadata.slot_mapping)\n            return super().forward(layer, query, key, value, kv_cache, attn_metadata, output, output_scale, output_block_scale)\n    attn_backend = subclass_attention_backend_with_overrides(name_prefix=prefix, attention_backend_cls=underlying_attn_backend, overrides={'get_builder_cls': lambda: CrossAttentionBuilder, 'get_impl_cls': lambda: CrossAttentionImpl, 'forward_includes_kv_cache_update': True})\n    return attn_backend",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/attention/cross_attention.py"
    },
    {
        "id": "_setup_kernel",
        "coords": [
            25,
            30,
            0
        ],
        "fiber": 24,
        "logic": "def _setup_kernel(self, layer: FusedMoE, w13: torch.Tensor, w2: torch.Tensor, w13_scale: torch.Tensor, w2_scale: torch.Tensor, w13_input_scale: torch.Tensor | None, w2_input_scale: torch.Tensor | None) -> None:\n    w13, w2, w13_scale, w2_scale = convert_to_fp8_moe_kernel_format(fp8_backend=self.fp8_backend, layer=layer, w13=w13, w2=w2, w13_scale=w13_scale, w2_scale=w2_scale, w13_input_scale=w13_input_scale, w2_input_scale=w2_input_scale)\n    replace_parameter(layer, 'w13_weight', w13)\n    replace_parameter(layer, 'w2_weight', w2)\n    replace_parameter(layer, f'w13_{self.weight_scale_name}', w13_scale)\n    replace_parameter(layer, f'w2_{self.weight_scale_name}', w2_scale)\n    self.moe_quant_config = self.get_fused_moe_quant_config(layer)\n    if self.moe_quant_config:\n        assert self.experts_cls is not None\n        self.moe_kernel = make_fp8_moe_kernel(moe_quant_config=self.moe_quant_config, moe_config=self.moe, fp8_backend=self.fp8_backend, experts_cls=self.experts_cls, routing_tables=layer._maybe_init_expert_routing_tables(), shared_experts=layer.shared_experts)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/fp8.py"
    },
    {
        "id": "_setup_kernel",
        "coords": [
            25,
            30,
            0
        ],
        "fiber": 24,
        "logic": "def _setup_kernel(self, layer: FusedMoE, w13: torch.Tensor, w2: torch.Tensor, w13_scale: torch.Tensor, w2_scale: torch.Tensor, w13_bias: torch.Tensor | None=None, w2_bias: torch.Tensor | None=None) -> None:\n    num_experts = self.num_experts\n    intermediate_size = self.intermediate_size\n    hidden_size = self.hidden_size\n    sf_block_size = 32\n    assert w13.dim() == 3 and w13.shape[0] == num_experts and (w13.shape[1] == intermediate_size * 2) and (w13.shape[2] == hidden_size // 2)\n    assert w13_scale.dim() == 3 and w13_scale.shape[0] == num_experts and (w13_scale.shape[1] == intermediate_size * 2) and (w13_scale.shape[2] == hidden_size // sf_block_size)\n    assert w2.dim() == 3 and w2.shape[0] == num_experts and (w2.shape[1] == hidden_size) and (w2.shape[2] == intermediate_size // 2)\n    assert w2_scale.dim() == 3 and w2_scale.shape[1] == hidden_size and (w2_scale.shape[2] == intermediate_size // sf_block_size)\n    if w13_bias is not None:\n        assert w13_bias.dim() == 2 and w13_bias.shape[0] == num_experts and (w13_bias.shape[1] == intermediate_size * 2)\n    if w2_bias is not None:\n        assert w2_bias.dim() == 2 and w2_bias.shape[0] == num_experts and (w2_bias.shape[1] == hidden_size)\n    w13, w2, w13_scale, w2_scale, w13_bias, w2_bias = convert_to_mxfp4_moe_kernel_format(mxfp4_backend=self.mxfp4_backend, layer=layer, w13_weight=w13, w2_weight=w2, w13_weight_scale=w13_scale, w2_weight_scale=w2_scale, w13_bias=w13_bias, w2_bias=w2_bias, _cache_permute_indices=self._cache_permute_indices)\n    if self.mxfp4_backend not in TRITON_BACKENDS:\n        replace_parameter(layer, 'w13_weight', w13)\n        replace_parameter(layer, 'w2_weight', w2)\n        replace_parameter(layer, 'w13_weight_scale', w13_scale)\n        replace_parameter(layer, 'w2_weight_scale', w2_scale)\n    else:\n        layer.w13_weight = w13\n        layer.w2_weight = w2\n        self.w13_precision_config = w13_scale\n        self.w2_precision_config = w2_scale\n    if w13_bias is not None and w2_bias is not None:\n        replace_parameter(layer, 'w13_bias', w13_bias)\n        replace_parameter(layer, 'w2_bias', w2_bias)\n    self.moe_quant_config = self.get_fused_moe_quant_config(layer)\n    if self.moe_quant_config is not None and self.experts_cls is not None:\n        self.moe_kernel = make_mxfp4_moe_kernel(moe_quant_config=self.moe_quant_config, moe_config=self.moe, mxfp4_backend=self.mxfp4_backend, experts_cls=self.experts_cls, routing_tables=layer._maybe_init_expert_routing_tables(), shared_experts=layer.shared_experts)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/mxfp4.py"
    },
    {
        "id": "_setup_kernel",
        "coords": [
            25,
            30,
            0
        ],
        "fiber": 24,
        "logic": "def _setup_kernel(self, layer: FusedMoE, w13: torch.Tensor, w2: torch.Tensor, w13_scale: torch.Tensor, w2_scale: torch.Tensor, w13_input_scale: torch.Tensor, w2_input_scale: torch.Tensor):\n    w13, w2, w13_scale, w2_scale = convert_to_fp8_moe_kernel_format(fp8_backend=self.fp8_backend, layer=layer, w13=w13, w2=w2, w13_scale=w13_scale, w2_scale=w2_scale, w13_input_scale=w13_input_scale, w2_input_scale=w2_input_scale)\n    replace_parameter(layer, 'w13_weight', w13)\n    replace_parameter(layer, 'w2_weight', w2)\n    replace_parameter(layer, 'w13_weight_scale', w13_scale)\n    replace_parameter(layer, 'w2_weight_scale', w2_scale)\n    self.moe_quant_config = self.get_fused_moe_quant_config(layer)\n    assert self.experts_cls is not None\n    self.moe_kernel = make_fp8_moe_kernel(moe_quant_config=self.moe_quant_config, moe_config=self.moe, fp8_backend=self.fp8_backend, experts_cls=self.experts_cls, routing_tables=layer._maybe_init_expert_routing_tables(), shared_experts=layer.shared_experts)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/modelopt.py"
    },
    {
        "id": "awq_dequantize_kernel",
        "coords": [
            10,
            6,
            12
        ],
        "fiber": 28,
        "logic": "@triton.jit\ndef awq_dequantize_kernel(qweight_ptr, scales_ptr, zeros_ptr, group_size, result_ptr, num_cols, num_rows, BLOCK_SIZE_X: tl.constexpr, BLOCK_SIZE_Y: tl.constexpr):\n    pid_x = tl.program_id(axis=0)\n    pid_y = tl.program_id(axis=1)\n    offsets_y = pid_y * BLOCK_SIZE_Y + tl.arange(0, BLOCK_SIZE_Y)\n    offsets_x = pid_x * BLOCK_SIZE_X + tl.arange(0, BLOCK_SIZE_X)\n    offsets = num_cols * offsets_y[:, None] + offsets_x[None, :]\n    masks_y = offsets_y < num_rows\n    masks_x = offsets_x < num_cols\n    masks = masks_y[:, None] & masks_x[None, :]\n    result_offsets_y = pid_y * BLOCK_SIZE_Y + tl.arange(0, BLOCK_SIZE_Y)\n    result_offsets_x = pid_x * BLOCK_SIZE_X * 8 + tl.arange(0, BLOCK_SIZE_X * 8)\n    result_offsets = 8 * num_cols * result_offsets_y[:, None] + result_offsets_x[None, :]\n    result_masks_y = result_offsets_y < num_rows\n    result_masks_x = result_offsets_x < num_cols * 8\n    result_masks = result_masks_y[:, None] & result_masks_x[None, :]\n    iweights = tl.load(qweight_ptr + offsets, masks, 0.0)\n    iweights = tl.interleave(iweights, iweights)\n    iweights = tl.interleave(iweights, iweights)\n    iweights = tl.interleave(iweights, iweights)\n    reverse_awq_order_tensor = ((tl.arange(0, 2) * 4)[None, :] + tl.arange(0, 4)[:, None]).reshape(8)\n    shifts = reverse_awq_order_tensor * 4\n    shifts = tl.broadcast_to(shifts[None, :], (BLOCK_SIZE_Y * BLOCK_SIZE_X, 8))\n    shifts = tl.reshape(shifts, (BLOCK_SIZE_Y, BLOCK_SIZE_X * 8))\n    iweights = iweights >> shifts & 15\n    zero_offsets_y = pid_y * BLOCK_SIZE_Y // group_size + tl.arange(0, 1)\n    zero_offsets_x = pid_x * BLOCK_SIZE_X + tl.arange(0, BLOCK_SIZE_X)\n    zero_offsets = num_cols * zero_offsets_y[:, None] + zero_offsets_x[None, :]\n    zero_masks_y = zero_offsets_y < num_rows // group_size\n    zero_masks_x = zero_offsets_x < num_cols\n    zero_masks = zero_masks_y[:, None] & zero_masks_x[None, :]\n    zeros = tl.load(zeros_ptr + zero_offsets, zero_masks, 0.0)\n    zeros = tl.interleave(zeros, zeros)\n    zeros = tl.interleave(zeros, zeros)\n    zeros = tl.interleave(zeros, zeros)\n    zeros = tl.broadcast_to(zeros, (BLOCK_SIZE_Y, BLOCK_SIZE_X * 8))\n    zeros = zeros >> shifts & 15\n    scale_offsets_y = pid_y * BLOCK_SIZE_Y // group_size + tl.arange(0, 1)\n    scale_offsets_x = pid_x * BLOCK_SIZE_X * 8 + tl.arange(0, BLOCK_SIZE_X * 8)\n    scale_offsets = num_cols * 8 * scale_offsets_y[:, None] + scale_offsets_x[None, :]\n    scale_masks_y = scale_offsets_y < num_rows // group_size\n    scale_masks_x = scale_offsets_x < num_cols * 8\n    scale_masks = scale_masks_y[:, None] & scale_masks_x[None, :]\n    scales = tl.load(scales_ptr + scale_offsets, scale_masks, 0.0)\n    scales = tl.broadcast_to(scales, (BLOCK_SIZE_Y, BLOCK_SIZE_X * 8))\n    iweights = (iweights - zeros) * scales\n    iweights = iweights.to(result_ptr.type.element_ty)\n    tl.store(result_ptr + result_offsets, iweights, result_masks)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/awq_triton.py"
    },
    {
        "id": "awq_gemm_kernel",
        "coords": [
            10,
            21,
            14
        ],
        "fiber": 14,
        "logic": "@triton.jit\ndef awq_gemm_kernel(a_ptr, b_ptr, c_ptr, zeros_ptr, scales_ptr, M, N, K, group_size, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, SPLIT_K: tl.constexpr):\n    pid = tl.program_id(axis=0)\n    pid_z = tl.program_id(1)\n    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)\n    pid_m = pid // num_pid_n\n    pid_n = pid % num_pid_n\n    accumulator_dtype = c_ptr.type.element_ty\n    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=accumulator_dtype)\n    reverse_awq_order_tensor = ((tl.arange(0, 2) * 4)[None, :] + tl.arange(0, 4)[:, None]).reshape(8)\n    shifts = reverse_awq_order_tensor * 4\n    shifts = tl.broadcast_to(shifts[None, :], (BLOCK_SIZE_K * (BLOCK_SIZE_N // 8), 8))\n    shifts = tl.reshape(shifts, (BLOCK_SIZE_K, BLOCK_SIZE_N))\n    offsets_am = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    masks_am = offsets_am < M\n    offsets_bn = pid_n * (BLOCK_SIZE_N // 8) + tl.arange(0, BLOCK_SIZE_N // 8)\n    masks_bn = offsets_bn < N // 8\n    offsets_zn = pid_n * (BLOCK_SIZE_N // 8) + tl.arange(0, BLOCK_SIZE_N // 8)\n    masks_zn = offsets_zn < N // 8\n    offsets_sn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    masks_sn = offsets_sn < N\n    offsets_k = pid_z * BLOCK_SIZE_K + tl.arange(0, BLOCK_SIZE_K)\n    offsets_a = K * offsets_am[:, None] + offsets_k[None, :]\n    offsets_b = N // 8 * offsets_k[:, None] + offsets_bn[None, :]\n    a_ptrs = a_ptr + offsets_a\n    b_ptrs = b_ptr + offsets_b\n    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K * SPLIT_K)):\n        masks_k = offsets_k < K\n        masks_a = masks_am[:, None] & masks_k[None, :]\n        a = tl.load(a_ptrs, mask=masks_a, other=0.0)\n        masks_b = masks_k[:, None] & masks_bn[None, :]\n        b = tl.load(b_ptrs, mask=masks_b, other=0.0)\n        b = tl.interleave(b, b)\n        b = tl.interleave(b, b)\n        b = tl.interleave(b, b)\n        offsets_szk = (BLOCK_SIZE_K * SPLIT_K * k + pid_z * BLOCK_SIZE_K) // group_size + tl.arange(0, 1)\n        offsets_z = N // 8 * offsets_szk[:, None] + offsets_zn[None, :]\n        masks_zk = offsets_szk < K // group_size\n        masks_z = masks_zk[:, None] & masks_zn[None, :]\n        zeros_ptrs = zeros_ptr + offsets_z\n        zeros = tl.load(zeros_ptrs, mask=masks_z, other=0.0)\n        zeros = tl.interleave(zeros, zeros)\n        zeros = tl.interleave(zeros, zeros)\n        zeros = tl.interleave(zeros, zeros)\n        zeros = tl.broadcast_to(zeros, (BLOCK_SIZE_K, BLOCK_SIZE_N))\n        offsets_s = N * offsets_szk[:, None] + offsets_sn[None, :]\n        masks_sk = offsets_szk < K // group_size\n        masks_s = masks_sk[:, None] & masks_sn[None, :]\n        scales_ptrs = scales_ptr + offsets_s\n        scales = tl.load(scales_ptrs, mask=masks_s, other=0.0)\n        scales = tl.broadcast_to(scales, (BLOCK_SIZE_K, BLOCK_SIZE_N))\n        b = b >> shifts & 15\n        zeros = zeros >> shifts & 15\n        b = (b - zeros) * scales\n        b = b.to(c_ptr.type.element_ty)\n        accumulator = tl.dot(a, b, accumulator, out_dtype=accumulator_dtype)\n        offsets_k += BLOCK_SIZE_K * SPLIT_K\n        a_ptrs += BLOCK_SIZE_K * SPLIT_K\n        b_ptrs += BLOCK_SIZE_K * SPLIT_K * (N // 8)\n    c = accumulator.to(c_ptr.type.element_ty)\n    offs_cm = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_cn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    c_ptrs = c_ptr + pid_z * N * M + N * offs_cm[:, None] + offs_cn[None, :]\n    c_mask = (offs_cm[:, None] < M) & (offs_cn[None, :] < N)\n    tl.store(c_ptrs, c, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/awq_triton.py"
    },
    {
        "id": "_import_petit_kernel",
        "coords": [
            11,
            1,
            22
        ],
        "fiber": 3,
        "logic": "def _import_petit_kernel() -> 'ModuleType':\n    \"\"\"\n    A helper function to handle the lazy import.\n    The first time this function is called, it will import the petit_kernel\n    library and store it in the global _petit_kernel variable.\n    Subsequent calls will return the already-loaded module directly.\n    \"\"\"\n    global _petit_kernel\n    if _petit_kernel is not None:\n        return _petit_kernel\n    try:\n        import petit_kernel\n        _petit_kernel = petit_kernel\n        return _petit_kernel\n    except ImportError:\n        raise ImportError(_PETIT_INSTALL_MSG) from None",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/utils/petit_utils.py"
    },
    {
        "id": "convert_to_nvfp4_linear_kernel_format",
        "coords": [
            13,
            9,
            17
        ],
        "fiber": 8,
        "logic": "def convert_to_nvfp4_linear_kernel_format(backend: NvFp4LinearBackend, layer: torch.nn.Module) -> None:\n    \"\"\"Convert layer to NVFP4 linear kernel format.\"\"\"\n    assert layer.weight_scale.dtype == torch.float8_e4m3fn, 'Weight Block scale must be represented as FP8-E4M3'\n    layer.weights_padding_cols = 0\n    if backend == NvFp4LinearBackend.MARLIN:\n        logger.warning_once('Your GPU does not have native support for FP4 computation but FP4 quantization is being used. Weight-only FP4 compression will be used leveraging the Marlin kernel. This may degrade performance for compute-heavy workloads.')\n        prepare_fp4_layer_for_marlin(layer)\n    elif backend == NvFp4LinearBackend.FLASHINFER_TRTLLM:\n        weight, weight_scale = prepare_weights_for_nvfp4_flashinfer_trtllm(layer.weight.data, layer.weight_scale.data)\n        layer.weight = torch.nn.Parameter(weight, requires_grad=False)\n        layer.weight_scale = torch.nn.Parameter(weight_scale, requires_grad=False)\n    elif backend == NvFp4LinearBackend.FBGEMM:\n        weight, weight_scale = prepare_weights_for_nvfp4_fbgemm(layer.weight.data, layer.weight_scale.data)\n        layer.weight = torch.nn.Parameter(weight, requires_grad=False)\n        layer.weight_scale = torch.nn.Parameter(weight_scale, requires_grad=False)\n    elif backend in (NvFp4LinearBackend.VLLM_CUTLASS, NvFp4LinearBackend.FLASHINFER_CUTLASS, NvFp4LinearBackend.FLASHINFER_CUDNN):\n        weight, weight_scale, weights_padding_cols = prepare_weights_for_nvfp4_cutlass(layer.weight.data, layer.weight_scale.data)\n        layer.weight = torch.nn.Parameter(weight, requires_grad=False)\n        layer.weight_scale = torch.nn.Parameter(weight_scale, requires_grad=False)\n        layer.weights_padding_cols = weights_padding_cols",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/utils/nvfp4_utils.py"
    },
    {
        "id": "group_broadcast",
        "coords": [
            25,
            20,
            29
        ],
        "fiber": 12,
        "logic": "def group_broadcast(t, shape):\n    for i, s in enumerate(shape):\n        t_dim_size = t.shape[i] if i < t.ndim else 1\n        if t_dim_size != s and t_dim_size != 1:\n            assert s % t_dim_size == 0\n            t = t.unsqueeze(i + 1).expand(*t.shape[:i + 1], s // t_dim_size, *t.shape[i + 1:]).flatten(i, i + 1)\n    return t",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/utils/quant_utils.py"
    },
    {
        "id": "prep_scale_for_group_broadcast",
        "coords": [
            21,
            18,
            21
        ],
        "fiber": 29,
        "logic": "def prep_scale_for_group_broadcast(scale: torch.Tensor, x: torch.Tensor, group_shape: GroupShape | None) -> torch.Tensor:\n    \"\"\"\n    Prepare the input quantization scale for group broadcasting.\n\n    Args:\n        scale: The scale tensor (scalar or 1D).\n        x: Target tensor whose shape determines broadcast dimensions.\n        group_shape: GroupShape to broadcast over.\n\n    Returns:\n        scale reshaped for correct broadcasting.\n    \"\"\"\n    if scale.numel() == 1:\n        return scale if group_shape is not None and group_shape.is_per_tensor() else scale.reshape(1, 1)\n    if scale.ndim == 1:\n        assert group_shape is not None, 'group_shape must be provided to correctly broadcast 1D scale'\n        rows, cols = _normalize_quant_group_shape(x, group_shape)\n        if rows == x.shape[-2]:\n            scale = scale.unsqueeze(-2)\n        elif cols == x.shape[-1]:\n            scale = scale.unsqueeze(-1)\n        else:\n            raise ValueError(f'1D scale with shape {scale.shape} cannot be broadcast to x with shape {x.shape}, group_shape={(rows, cols)}')\n    return scale",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/utils/quant_utils.py"
    },
    {
        "id": "_setup_kernel_via_oracle",
        "coords": [
            18,
            21,
            21
        ],
        "fiber": 29,
        "logic": "def _setup_kernel_via_oracle(self, layer: FusedMoE):\n    \"\"\"Setup kernel using oracle functions for w_mxfp4 scheme.\"\"\"\n    w13 = layer.w13_weight\n    w2 = layer.w2_weight\n    w13_scale = layer.w13_weight_scale\n    w2_scale = layer.w2_weight_scale\n    w13_bias = getattr(layer, 'w13_bias', None)\n    w2_bias = getattr(layer, 'w2_bias', None)\n    w13, w2, w13_scale, w2_scale, w13_bias, w2_bias = convert_to_mxfp4_moe_kernel_format(mxfp4_backend=self.mxfp4_backend, layer=layer, w13_weight=w13, w2_weight=w2, w13_weight_scale=w13_scale, w2_weight_scale=w2_scale, w13_bias=w13_bias, w2_bias=w2_bias)\n    if self.mxfp4_backend not in TRITON_BACKENDS:\n        replace_parameter(layer, 'w13_weight', w13)\n        replace_parameter(layer, 'w2_weight', w2)\n        replace_parameter(layer, 'w13_weight_scale', w13_scale)\n        replace_parameter(layer, 'w2_weight_scale', w2_scale)\n    else:\n        layer.w13_weight = w13\n        layer.w2_weight = w2\n        self.w13_precision_config = w13_scale\n        self.w2_precision_config = w2_scale\n    if w13_bias is not None and w2_bias is not None:\n        replace_parameter(layer, 'w13_bias', w13_bias)\n        replace_parameter(layer, 'w2_bias', w2_bias)\n    self.moe_quant_config = self.get_fused_moe_quant_config(layer)\n    if self.moe_quant_config is not None and self.experts_cls is not None:\n        self.moe_kernel = make_mxfp4_moe_kernel(moe_quant_config=self.moe_quant_config, moe_config=self.moe, mxfp4_backend=self.mxfp4_backend, experts_cls=self.experts_cls, routing_tables=layer._maybe_init_expert_routing_tables(), shared_experts=layer.shared_experts)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/quark/quark_moe.py"
    },
    {
        "id": "_apply_aiter_kernel",
        "coords": [
            5,
            14,
            0
        ],
        "fiber": 19,
        "logic": "def _apply_aiter_kernel(self, layer: torch.nn.Module, x: torch.Tensor, bias: torch.Tensor | None=None) -> torch.Tensor:\n    M = x.shape[0]\n    out_dtype = x.dtype if self.out_dtype is None else self.out_dtype\n    input_scale = layer.input_scale\n    x_fp8 = (x / input_scale).clamp(self.fp8_min, self.fp8_max).to(self.fp8_dtype)\n    x_scales = input_scale.expand(M, 1).to(dtype=torch.float32, device=x.device)\n    y = rocm_aiter_ops.gemm_a8wfp4(x_fp8, layer.weight, x_scales, layer.weight_scale, out_dtype)\n    if bias is not None:\n        y = y + bias\n    return y",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/quark/schemes/quark_w4a8_mxfp4_fp8.py"
    },
    {
        "id": "scaled_mm_kernel",
        "coords": [
            13,
            13,
            3
        ],
        "fiber": 29,
        "logic": "@triton.jit\ndef scaled_mm_kernel(a_ptr, b_ptr, scale_a_ptr, scale_b_ptr, c_ptr, bias_ptr, M, N, K, stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn, ACCUMULATOR_DTYPE: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, BLOCK_SIZE_SCALE_A: tl.constexpr, BLOCK_SIZE_SCALE_B: tl.constexpr):\n    pid = tl.program_id(axis=0)\n    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)\n    pid_m = pid // num_pid_n\n    pid_n = pid % num_pid_n\n    accumulator_dtype = ACCUMULATOR_DTYPE\n    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=accumulator_dtype)\n    offsets_am = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M).to(tl.int64)\n    masks_am = offsets_am < M\n    offsets_bn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N).to(tl.int64)\n    masks_bn = offsets_bn < N\n    offsets_k = tl.arange(0, BLOCK_SIZE_K).to(tl.int64)\n    offsets_a = stride_am * offsets_am[:, None] + stride_ak * offsets_k[None, :]\n    offsets_b = stride_bk * offsets_k[:, None] + stride_bn * offsets_bn[None, :]\n    offsets_scale_am = tl.arange(0, BLOCK_SIZE_SCALE_A) + (BLOCK_SIZE_SCALE_A > 1) * pid_m * BLOCK_SIZE_M\n    masks_scale_am = offsets_scale_am < M\n    offsets_scale_bn = tl.arange(0, BLOCK_SIZE_SCALE_B) + (BLOCK_SIZE_SCALE_B > 1) * pid_n * BLOCK_SIZE_N\n    masks_scale_bn = offsets_scale_bn < N\n    a_ptrs = a_ptr + offsets_a\n    b_ptrs = b_ptr + offsets_b\n    scale_a_ptrs = scale_a_ptr + offsets_scale_am\n    scale_b_ptrs = scale_b_ptr + offsets_scale_bn\n    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K)):\n        masks_k = offsets_k < K\n        masks_a = masks_am[:, None] & masks_k[None, :]\n        a = tl.load(a_ptrs, mask=masks_a)\n        masks_b = masks_k[:, None] & masks_bn[None, :]\n        b = tl.load(b_ptrs, mask=masks_b)\n        accumulator = tl.dot(a, b, accumulator, out_dtype=accumulator_dtype)\n        offsets_k += BLOCK_SIZE_K\n        a_ptrs += BLOCK_SIZE_K * stride_ak\n        b_ptrs += BLOCK_SIZE_K * stride_bk\n    masks_scale_a = masks_scale_am[:, None] & (tl.arange(0, 1) < 1)[:, None]\n    scale_a = tl.load(scale_a_ptrs[:, None], masks_scale_a)\n    scale_a = scale_a.broadcast_to((BLOCK_SIZE_M, 1))\n    accumulator = scale_a * accumulator.to(tl.float32)\n    masks_scale_b = masks_scale_bn[:, None] & (tl.arange(0, 1) < 1)[None, :]\n    scale_b = tl.load(scale_b_ptrs[:, None], masks_scale_b)\n    scale_b = scale_b.broadcast_to((BLOCK_SIZE_N, 1))\n    accumulator = scale_b.T * accumulator.to(tl.float32)\n    c = accumulator.to(c_ptr.type.element_ty)\n    if bias_ptr:\n        offsets_bias = offsets_bn\n        bias_ptrs = bias_ptr + offsets_bias\n        bias_mask = offsets_bias < N\n        bias = tl.load(bias_ptrs, bias_mask)\n        c += bias\n    offs_cm = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M).to(tl.int64)\n    offs_cn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N).to(tl.int64)\n    offs_cm = offs_cm.to(tl.int64)\n    offs_cn = offs_cn.to(tl.int64)\n    c_ptrs = c_ptr + stride_cm * offs_cm[:, None] + stride_cn * offs_cn[None, :]\n    c_mask = (offs_cm[:, None] < M) & (offs_cn[None, :] < N)\n    tl.store(c_ptrs, c, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/quantization/compressed_tensors/triton_scaled_mm.py"
    },
    {
        "id": "chunk_local_cumsum_scalar_kernel",
        "coords": [
            26,
            19,
            8
        ],
        "fiber": 22,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps) for num_warps in [1, 2, 4, 8]], key=['B', 'H', 'BT', 'IS_VARLEN', 'REVERSE'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_local_cumsum_scalar_kernel(s, o, cu_seqlens, chunk_indices, T, B: tl.constexpr, H: tl.constexpr, BT: tl.constexpr, REVERSE: tl.constexpr, IS_VARLEN: tl.constexpr, HEAD_FIRST: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    if HEAD_FIRST:\n        p_s = tl.make_block_ptr(s + bos * H + i_h * T, (T,), (1,), (i_t * BT,), (BT,), (0,))\n        p_o = tl.make_block_ptr(o + bos * H + i_h * T, (T,), (1,), (i_t * BT,), (BT,), (0,))\n    else:\n        p_s = tl.make_block_ptr(s + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n        p_o = tl.make_block_ptr(o + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n    b_s = tl.load(p_s, boundary_check=(0,)).to(tl.float32)\n    b_o = tl.cumsum(b_s, axis=0)\n    if REVERSE:\n        b_z = tl.sum(b_s, axis=0)\n        b_o = -b_o + b_z[None] + b_s\n    tl.store(p_o, b_o.to(p_o.dtype.element_ty), boundary_check=(0,))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/cumsum.py"
    },
    {
        "id": "chunk_local_cumsum_vector_kernel",
        "coords": [
            4,
            12,
            10
        ],
        "fiber": 26,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({'BS': BS}, num_warps=num_warps) for BS in BS_LIST for num_warps in [2, 4, 8]], key=['B', 'H', 'S', 'BT', 'IS_VARLEN', 'REVERSE'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_local_cumsum_vector_kernel(s, o, cu_seqlens, chunk_indices, T, B: tl.constexpr, H: tl.constexpr, S: tl.constexpr, BT: tl.constexpr, BS: tl.constexpr, REVERSE: tl.constexpr, IS_VARLEN: tl.constexpr, HEAD_FIRST: tl.constexpr):\n    i_s, i_t, i_bh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    o_i = tl.arange(0, BT)\n    if REVERSE:\n        m_s = tl.where(o_i[:, None] <= o_i[None, :], 1.0, 0.0)\n    else:\n        m_s = tl.where(o_i[:, None] >= o_i[None, :], 1.0, 0.0)\n    if HEAD_FIRST:\n        p_s = tl.make_block_ptr(s + (bos * H + i_h * T) * S, (T, S), (S, 1), (i_t * BT, i_s * BS), (BT, BS), (1, 0))\n        p_o = tl.make_block_ptr(o + (bos * H + i_h * T) * S, (T, S), (S, 1), (i_t * BT, i_s * BS), (BT, BS), (1, 0))\n    else:\n        p_s = tl.make_block_ptr(s + (bos * H + i_h) * S, (T, S), (H * S, 1), (i_t * BT, i_s * BS), (BT, BS), (1, 0))\n        p_o = tl.make_block_ptr(o + (bos * H + i_h) * S, (T, S), (H * S, 1), (i_t * BT, i_s * BS), (BT, BS), (1, 0))\n    b_s = tl.load(p_s, boundary_check=(0, 1)).to(tl.float32)\n    b_o = tl.dot(m_s, b_s, allow_tf32=False)\n    tl.store(p_o, b_o.to(p_o.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/cumsum.py"
    },
    {
        "id": "recompute_w_u_fwd_kernel",
        "coords": [
            11,
            11,
            29
        ],
        "fiber": 20,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps, num_stages=num_stages) for num_warps in [2, 4, 8] for num_stages in [2, 3, 4]], key=['H', 'K', 'V', 'BT', 'BK', 'BV', 'IS_VARLEN'])\n@triton.jit(do_not_specialize=['T'])\ndef recompute_w_u_fwd_kernel(k, v, beta, w, u, A, g, cu_seqlens, chunk_indices, T, H: tl.constexpr, Hg: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, IS_VARLEN: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    p_beta = tl.make_block_ptr(beta + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n    p_g = tl.make_block_ptr(g + (bos * H + i_h), (T,), (H,), (i_t * BT,), (BT,), (0,))\n    p_A = tl.make_block_ptr(A + (bos * H + i_h) * BT, (T, BT), (H * BT, 1), (i_t * BT, 0), (BT, BT), (1, 0))\n    b_beta = tl.load(p_beta, boundary_check=(0,))\n    b_A = tl.load(p_A, boundary_check=(0, 1))\n    b_g = tl.exp(tl.load(p_g, boundary_check=(0,)))\n    for i_v in range(tl.cdiv(V, BV)):\n        p_v = tl.make_block_ptr(v + (bos * H + i_h) * V, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n        p_u = tl.make_block_ptr(u + (bos * H + i_h) * V, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n        b_v = tl.load(p_v, boundary_check=(0, 1))\n        b_vb = (b_v * b_beta[:, None]).to(b_v.dtype)\n        b_u = tl.dot(b_A, b_vb, allow_tf32=False)\n        tl.store(p_u, b_u.to(p_u.dtype.element_ty), boundary_check=(0, 1))\n    for i_k in range(tl.cdiv(K, BK)):\n        p_k = tl.make_block_ptr(k + (bos * Hg + i_h // (H // Hg)) * K, (T, K), (Hg * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        p_w = tl.make_block_ptr(w + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        b_k = tl.load(p_k, boundary_check=(0, 1))\n        b_kb = (b_k * b_beta[:, None] * b_g[:, None]).to(b_k.dtype)\n        b_w = tl.dot(b_A, b_kb)\n        tl.store(p_w, b_w.to(p_w.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/wy_fast.py"
    },
    {
        "id": "fused_recurrent_gated_delta_rule_fwd_kernel",
        "coords": [
            5,
            3,
            16
        ],
        "fiber": 24,
        "logic": "@triton.heuristics({'USE_INITIAL_STATE': lambda args: args['h0'] is not None, 'IS_VARLEN': lambda args: args['cu_seqlens'] is not None, 'IS_CONTINUOUS_BATCHING': lambda args: args['ssm_state_indices'] is not None, 'IS_SPEC_DECODING': lambda args: args['num_accepted_tokens'] is not None})\n@triton.jit(do_not_specialize=['N', 'T'])\ndef fused_recurrent_gated_delta_rule_fwd_kernel(q, k, v, g, beta, o, h0, ht, cu_seqlens, ssm_state_indices, num_accepted_tokens, scale, N: tl.int64, T: tl.int64, B: tl.constexpr, H: tl.constexpr, HV: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, stride_init_state_token: tl.constexpr, stride_final_state_token: tl.constexpr, stride_indices_seq: tl.constexpr, stride_indices_tok: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, INPLACE_FINAL_STATE: tl.constexpr, IS_BETA_HEADWISE: tl.constexpr, USE_QK_L2NORM_IN_KERNEL: tl.constexpr, IS_VARLEN: tl.constexpr, IS_CONTINUOUS_BATCHING: tl.constexpr, IS_SPEC_DECODING: tl.constexpr, IS_KDA: tl.constexpr):\n    i_k, i_v, i_nh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_n, i_hv = (i_nh // HV, i_nh % HV)\n    i_h = i_hv // (HV // H)\n    if IS_VARLEN:\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))\n        all = T\n        T = eos - bos\n    else:\n        bos, eos = (i_n * T, i_n * T + T)\n        all = B * T\n    if T == 0:\n        return\n    o_k = i_k * BK + tl.arange(0, BK)\n    o_v = i_v * BV + tl.arange(0, BV)\n    p_q = q + (bos * H + i_h) * K + o_k\n    p_k = k + (bos * H + i_h) * K + o_k\n    p_v = v + (bos * HV + i_hv) * V + o_v\n    if IS_BETA_HEADWISE:\n        p_beta = beta + (bos * HV + i_hv) * V + o_v\n    else:\n        p_beta = beta + bos * HV + i_hv\n    if not IS_KDA:\n        p_g = g + bos * HV + i_hv\n    else:\n        p_gk = g + (bos * HV + i_hv) * K + o_k\n    p_o = o + ((i_k * all + bos) * HV + i_hv) * V + o_v\n    mask_k = o_k < K\n    mask_v = o_v < V\n    mask_h = mask_v[:, None] & mask_k[None, :]\n    b_h = tl.zeros([BV, BK], dtype=tl.float32)\n    if USE_INITIAL_STATE:\n        if IS_CONTINUOUS_BATCHING:\n            if IS_SPEC_DECODING:\n                i_t = tl.load(num_accepted_tokens + i_n).to(tl.int64) - 1\n            else:\n                i_t = 0\n            state_idx = tl.load(ssm_state_indices + i_n * stride_indices_seq + i_t).to(tl.int64)\n            if state_idx < 0:\n                return\n            p_h0 = h0 + state_idx * stride_init_state_token\n        else:\n            p_h0 = h0 + bos * HV * V * K\n        p_h0 = p_h0 + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n        b_h += tl.load(p_h0, mask=mask_h, other=0).to(tl.float32)\n    for i_t in range(0, T):\n        b_q = tl.load(p_q, mask=mask_k, other=0).to(tl.float32)\n        b_k = tl.load(p_k, mask=mask_k, other=0).to(tl.float32)\n        b_v = tl.load(p_v, mask=mask_v, other=0).to(tl.float32)\n        if USE_QK_L2NORM_IN_KERNEL:\n            b_q = b_q / tl.sqrt(tl.sum(b_q * b_q) + 1e-06)\n            b_k = b_k / tl.sqrt(tl.sum(b_k * b_k) + 1e-06)\n        b_q = b_q * scale\n        if not IS_KDA:\n            b_g = tl.load(p_g).to(tl.float32)\n            b_h *= exp(b_g)\n        else:\n            b_gk = tl.load(p_gk).to(tl.float32)\n            b_h *= exp(b_gk[None, :])\n        b_v -= tl.sum(b_h * b_k[None, :], 1)\n        if IS_BETA_HEADWISE:\n            b_beta = tl.load(p_beta, mask=mask_v, other=0).to(tl.float32)\n        else:\n            b_beta = tl.load(p_beta).to(tl.float32)\n        b_v *= b_beta\n        b_h += b_v[:, None] * b_k[None, :]\n        b_o = tl.sum(b_h * b_q[None, :], 1)\n        tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=mask_v)\n        if INPLACE_FINAL_STATE:\n            final_state_idx = tl.load(ssm_state_indices + i_n * stride_indices_seq + i_t).to(tl.int64)\n            if final_state_idx >= 0:\n                p_ht = ht + final_state_idx * stride_final_state_token\n                p_ht = p_ht + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n                tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)\n        else:\n            p_ht = ht + (bos + i_t) * stride_final_state_token\n            p_ht = p_ht + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n            tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)\n        p_q += H * K\n        p_k += H * K\n        p_o += HV * V\n        p_v += HV * V\n        if not IS_KDA:\n            p_g += HV\n        else:\n            p_gk += HV * K\n        p_beta += HV * (V if IS_BETA_HEADWISE else 1)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/fused_recurrent.py"
    },
    {
        "id": "fused_recurrent_gated_delta_rule_packed_decode_kernel",
        "coords": [
            22,
            12,
            4
        ],
        "fiber": 7,
        "logic": "@triton.jit\ndef fused_recurrent_gated_delta_rule_packed_decode_kernel(mixed_qkv, a, b, A_log, dt_bias, o, h0, ht, ssm_state_indices, scale, stride_mixed_qkv_tok: tl.constexpr, stride_a_tok: tl.constexpr, stride_b_tok: tl.constexpr, stride_init_state_token: tl.constexpr, stride_final_state_token: tl.constexpr, stride_indices_seq: tl.constexpr, H: tl.constexpr, HV: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, SOFTPLUS_THRESHOLD: tl.constexpr, USE_QK_L2NORM_IN_KERNEL: tl.constexpr):\n    i_v, i_nh = (tl.program_id(0), tl.program_id(1))\n    i_n, i_hv = (i_nh // HV, i_nh % HV)\n    i_h = i_hv // (HV // H)\n    o_k = tl.arange(0, BK)\n    o_v = i_v * BV + tl.arange(0, BV)\n    mask_k = o_k < K\n    mask_v = o_v < V\n    mask_h = mask_v[:, None] & mask_k[None, :]\n    state_idx = tl.load(ssm_state_indices + i_n * stride_indices_seq).to(tl.int64)\n    p_o = o + (i_n * HV + i_hv) * V + o_v\n    if state_idx < 0:\n        zero = tl.zeros([BV], dtype=tl.float32).to(p_o.dtype.element_ty)\n        tl.store(p_o, zero, mask=mask_v)\n        return\n    p_h0 = h0 + state_idx * stride_init_state_token\n    p_h0 = p_h0 + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n    b_h = tl.load(p_h0, mask=mask_h, other=0).to(tl.float32)\n    p_mixed = mixed_qkv + i_n * stride_mixed_qkv_tok\n    q_off = i_h * K + o_k\n    k_off = H * K + i_h * K + o_k\n    v_off = 2 * H * K + i_hv * V + o_v\n    b_q = tl.load(p_mixed + q_off, mask=mask_k, other=0).to(tl.float32)\n    b_k = tl.load(p_mixed + k_off, mask=mask_k, other=0).to(tl.float32)\n    b_v = tl.load(p_mixed + v_off, mask=mask_v, other=0).to(tl.float32)\n    if USE_QK_L2NORM_IN_KERNEL:\n        b_q = b_q / tl.sqrt(tl.sum(b_q * b_q) + 1e-06)\n        b_k = b_k / tl.sqrt(tl.sum(b_k * b_k) + 1e-06)\n    b_q = b_q * scale\n    a_val = tl.load(a + i_n * stride_a_tok + i_hv).to(tl.float32)\n    b_val = tl.load(b + i_n * stride_b_tok + i_hv).to(tl.float32)\n    A_log_val = tl.load(A_log + i_hv).to(tl.float32)\n    dt_bias_val = tl.load(dt_bias + i_hv).to(tl.float32)\n    x = a_val + dt_bias_val\n    softplus_x = tl.where(x <= SOFTPLUS_THRESHOLD, tl.log(1.0 + tl.exp(x)), x)\n    g_val = -tl.exp(A_log_val) * softplus_x\n    beta_val = tl.sigmoid(b_val).to(b.dtype.element_ty).to(tl.float32)\n    b_h *= exp(g_val)\n    b_v -= tl.sum(b_h * b_k[None, :], 1)\n    b_v *= beta_val\n    b_h += b_v[:, None] * b_k[None, :]\n    b_o = tl.sum(b_h * b_q[None, :], 1)\n    tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=mask_v)\n    p_ht = ht + state_idx * stride_final_state_token\n    p_ht = p_ht + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n    tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/fused_recurrent.py"
    },
    {
        "id": "chunk_fwd_kernel_o",
        "coords": [
            24,
            1,
            21
        ],
        "fiber": 15,
        "logic": "@triton.heuristics({'USE_G': lambda args: args['g'] is not None, 'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({'BK': BK, 'BV': BV}, num_warps=num_warps, num_stages=num_stages) for BK in BKV_LIST for BV in BKV_LIST for num_warps in NUM_WARPS for num_stages in [2, 3, 4]], key=['H', 'K', 'V', 'BT'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_fwd_kernel_o(q, k, v, h, g, o, cu_seqlens, chunk_indices, scale, T, H: tl.constexpr, Hg: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, USE_G: tl.constexpr, IS_VARLEN: tl.constexpr):\n    i_v, i_t, i_bh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_tg = i_t\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n        NT = tl.cdiv(T, BT)\n    else:\n        NT = tl.cdiv(T, BT)\n        i_tg = i_b * NT + i_t\n        bos, eos = (i_b * T, i_b * T + T)\n    q += (bos * Hg + i_h // (H // Hg)) * K\n    k += (bos * Hg + i_h // (H // Hg)) * K\n    v += (bos * H + i_h) * V\n    o += (bos * H + i_h) * V\n    h += (i_tg * H + i_h).to(tl.int64) * V * K\n    b_o = tl.zeros([BT, BV], dtype=tl.float32)\n    b_A = tl.zeros([BT, BT], dtype=tl.float32)\n    for i_k in range(tl.cdiv(K, BK)):\n        p_q = tl.make_block_ptr(q, (T, K), (Hg * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        p_k = tl.make_block_ptr(k, (K, T), (1, Hg * K), (i_k * BK, i_t * BT), (BK, BT), (0, 1))\n        p_h = tl.make_block_ptr(h, (V, K), (K, 1), (i_v * BV, i_k * BK), (BV, BK), (1, 0))\n        b_q = tl.load(p_q, boundary_check=(0, 1))\n        b_k = tl.load(p_k, boundary_check=(0, 1))\n        b_h = tl.load(p_h, boundary_check=(0, 1))\n        b_o += tl.dot(b_q, tl.trans(b_h))\n        b_A += tl.dot(b_q, b_k)\n    if USE_G:\n        g += bos * H + i_h\n        p_g = tl.make_block_ptr(g, (T,), (H,), (i_t * BT,), (BT,), (0,))\n        b_g = tl.load(p_g, boundary_check=(0,))\n        b_o = b_o * exp(b_g)[:, None]\n        b_A = b_A * exp(b_g[:, None] - b_g[None, :])\n    o_t = i_t * BT + tl.arange(0, BT)\n    m_t = o_t < T\n    m_A = (o_t[:, None] >= o_t[None, :]) & (m_t[:, None] & m_t)\n    b_A = tl.where(m_A, b_A, 0)\n    p_v = tl.make_block_ptr(v, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n    p_o = tl.make_block_ptr(o, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n    b_v = tl.load(p_v, boundary_check=(0, 1))\n    b_o = b_o * scale + tl.dot(b_A.to(b_v.dtype), b_v) * scale\n    tl.store(p_o, b_o.to(p_o.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/chunk_o.py"
    },
    {
        "id": "fused_sigmoid_gating_delta_rule_update_kernel",
        "coords": [
            11,
            13,
            8
        ],
        "fiber": 1,
        "logic": "@triton.heuristics({'USE_INITIAL_STATE': lambda args: args['h0'] is not None, 'IS_VARLEN': lambda args: args['cu_seqlens'] is not None, 'IS_CONTINUOUS_BATCHING': lambda args: args['ssm_state_indices'] is not None, 'IS_SPEC_DECODING': lambda args: args['num_accepted_tokens'] is not None})\n@triton.jit(do_not_specialize=['N', 'T'])\ndef fused_sigmoid_gating_delta_rule_update_kernel(A_log, a, b, dt_bias, beta, threshold, q, k, v, o, h0, ht, cu_seqlens, ssm_state_indices, num_accepted_tokens, scale, N: tl.int64, T: tl.int64, B: tl.constexpr, H: tl.constexpr, HV: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, stride_init_state_token: tl.constexpr, stride_final_state_token: tl.constexpr, stride_indices_seq: tl.constexpr, stride_indices_tok: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, INPLACE_FINAL_STATE: tl.constexpr, USE_QK_L2NORM_IN_KERNEL: tl.constexpr, IS_VARLEN: tl.constexpr, IS_CONTINUOUS_BATCHING: tl.constexpr, IS_SPEC_DECODING: tl.constexpr, IS_KDA: tl.constexpr):\n    i_k, i_v, i_nh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_n, i_hv = (i_nh // HV, i_nh % HV)\n    i_h = i_hv // (HV // H)\n    if IS_VARLEN:\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))\n        all = T\n        T = eos - bos\n    else:\n        bos, eos = (i_n * T, i_n * T + T)\n        all = B * T\n    if T == 0:\n        return\n    o_k = i_k * BK + tl.arange(0, BK)\n    o_v = i_v * BV + tl.arange(0, BV)\n    p_q = q + (bos * H + i_h) * K + o_k\n    p_k = k + (bos * H + i_h) * K + o_k\n    p_v = v + (bos * HV + i_hv) * V + o_v\n    p_A_log = A_log + i_hv\n    if not IS_KDA:\n        p_a = a + bos * HV + i_hv\n        p_dt_bias = dt_bias + i_hv\n    else:\n        p_a = a + (bos * HV + i_hv) * K + o_k\n        p_dt_bias = dt_bias + i_hv * K + o_k\n    p_b = b + bos * HV + i_hv\n    p_o = o + ((i_k * all + bos) * HV + i_hv) * V + o_v\n    mask_k = o_k < K\n    mask_v = o_v < V\n    mask_h = mask_v[:, None] & mask_k[None, :]\n    b_h = tl.zeros([BV, BK], dtype=tl.float32)\n    if USE_INITIAL_STATE:\n        if IS_CONTINUOUS_BATCHING:\n            if IS_SPEC_DECODING:\n                i_t = tl.load(num_accepted_tokens + i_n).to(tl.int64) - 1\n            else:\n                i_t = 0\n            state_idx = tl.load(ssm_state_indices + i_n * stride_indices_seq + i_t).to(tl.int64)\n            if state_idx < 0:\n                return\n            p_h0 = h0 + state_idx * stride_init_state_token\n        else:\n            p_h0 = h0 + bos * HV * V * K\n        p_h0 = p_h0 + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n        b_h += tl.load(p_h0, mask=mask_h, other=0).to(tl.float32)\n    for i_t in range(0, T):\n        b_q = tl.load(p_q, mask=mask_k, other=0).to(tl.float32)\n        b_k = tl.load(p_k, mask=mask_k, other=0).to(tl.float32)\n        b_v = tl.load(p_v, mask=mask_v, other=0).to(tl.float32)\n        b_b = tl.load(p_b).to(tl.float32)\n        x = tl.load(p_a).to(tl.float32) + tl.load(p_dt_bias).to(tl.float32)\n        softplus_x = tl.where(beta * x <= threshold, 1 / beta * tl.log(1 + tl.exp(beta * x)), x)\n        b_g = -tl.exp(tl.load(p_A_log).to(tl.float32)) * softplus_x\n        b_beta = tl.sigmoid(b_b.to(tl.float32))\n        if USE_QK_L2NORM_IN_KERNEL:\n            b_q = b_q * tl.rsqrt(tl.sum(b_q * b_q) + 1e-06)\n            b_k = b_k * tl.rsqrt(tl.sum(b_k * b_k) + 1e-06)\n        b_q = b_q * scale\n        if not IS_KDA:\n            b_h *= tl.exp(b_g)\n        else:\n            b_h *= tl.exp(b_g[None, :])\n        b_v -= tl.sum(b_h * b_k[None, :], 1)\n        b_v *= b_beta\n        b_h += b_v[:, None] * b_k[None, :]\n        b_o = tl.sum(b_h * b_q[None, :], 1)\n        tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=mask_v)\n        if INPLACE_FINAL_STATE:\n            final_state_idx = tl.load(ssm_state_indices + i_n * stride_indices_seq + i_t).to(tl.int64)\n            if final_state_idx >= 0:\n                p_ht = ht + final_state_idx * stride_final_state_token\n                p_ht = p_ht + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n                tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)\n        else:\n            p_ht = ht + (bos + i_t) * stride_final_state_token\n            p_ht = p_ht + i_hv * V * K + o_v[:, None] * K + o_k[None, :]\n            tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)\n        p_q += H * K\n        p_k += H * K\n        p_o += HV * V\n        p_v += HV * V\n        p_b += HV\n        p_a += HV",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/fused_sigmoid_gating.py"
    },
    {
        "id": "chunk_scaled_dot_kkt_fwd_kernel",
        "coords": [
            2,
            20,
            12
        ],
        "fiber": 3,
        "logic": "@triton.heuristics({'USE_G': lambda args: args['g'] is not None, 'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({'BK': BK}, num_warps=num_warps, num_stages=num_stages) for BK in [32, 64, 128] for num_warps in [2, 4, 8] for num_stages in [2, 3, 4]], key=['H', 'K', 'BT', 'IS_VARLEN'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_scaled_dot_kkt_fwd_kernel(k, beta, g, A, cu_seqlens, chunk_indices, T, H: tl.constexpr, Hg: tl.constexpr, K: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, IS_VARLEN: tl.constexpr, USE_G: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    o_t = i_t * BT + tl.arange(0, BT)\n    m_t = o_t < T\n    p_beta = tl.make_block_ptr(beta + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n    b_beta = tl.load(p_beta, boundary_check=(0,))\n    b_A = tl.zeros([BT, BT], dtype=tl.float32)\n    for i_k in range(tl.cdiv(K, BK)):\n        p_k = tl.make_block_ptr(k + (bos * Hg + i_h // (H // Hg)) * K, (T, K), (Hg * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        b_k = tl.load(p_k, boundary_check=(0, 1))\n        b_kb = b_k * b_beta[:, None]\n        b_A += tl.dot(b_kb.to(b_k.dtype), tl.trans(b_k))\n    if USE_G:\n        p_g = tl.make_block_ptr(g + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n        b_g = tl.load(p_g, boundary_check=(0,))\n        b_g_diff = b_g[:, None] - b_g[None, :]\n        b_A = b_A * exp(b_g_diff)\n    m_A = (o_t[:, None] > o_t[None, :]) & (m_t[:, None] & m_t)\n    b_A = tl.where(m_A, b_A, 0)\n    p_A = tl.make_block_ptr(A + (bos * H + i_h) * BT, (T, BT), (BT * H, 1), (i_t * BT, 0), (BT, BT), (1, 0))\n    tl.store(p_A, b_A.to(p_A.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/chunk_scaled_dot_kkt.py"
    },
    {
        "id": "layer_norm_fwd_kernel",
        "coords": [
            8,
            11,
            19
        ],
        "fiber": 7,
        "logic": "@triton.heuristics({'HAS_BIAS': lambda args: args['B'] is not None, 'HAS_Z': lambda args: args['Z'] is not None})\n@triton.jit\ndef layer_norm_fwd_kernel(X, Y, W, B, Z, Mean, Rstd, stride_x_row, stride_y_row, stride_z_row, M, N: tl.constexpr, eps, BLOCK_N: tl.constexpr, ROWS_PER_BLOCK: tl.constexpr, HAS_BIAS: tl.constexpr, HAS_Z: tl.constexpr, NORM_BEFORE_GATE: tl.constexpr, IS_RMS_NORM: tl.constexpr, ACTIVATION: tl.constexpr):\n    row_start = tl.program_id(0) * ROWS_PER_BLOCK\n    group = tl.program_id(1)\n    rows = row_start + tl.arange(0, ROWS_PER_BLOCK)\n    cols = tl.arange(0, BLOCK_N)\n    row_offsets = rows[:, None] * stride_x_row\n    col_offsets = cols[None, :] + group * N\n    X_base = X + row_offsets + col_offsets\n    Y_base = Y + rows[:, None] * stride_y_row + col_offsets\n    row_mask = rows[:, None] < M\n    col_mask = cols[None, :] < N\n    mask = row_mask & col_mask\n    x = tl.load(X_base, mask=mask, other=0.0).to(tl.float32)\n    if HAS_Z and (not NORM_BEFORE_GATE):\n        Z_base = Z + rows[:, None] * stride_z_row + col_offsets\n        z = tl.load(Z_base, mask=mask, other=0.0).to(tl.float32)\n        if ACTIVATION == 'swish' or ACTIVATION == 'silu':\n            x *= z * tl.sigmoid(z)\n        elif ACTIVATION == 'sigmoid':\n            x *= tl.sigmoid(z)\n    if not IS_RMS_NORM:\n        mean = tl.sum(x, axis=1) / N\n        mean_offsets = group * M + rows\n        mean_mask = rows < M\n        tl.store(Mean + mean_offsets, mean, mask=mean_mask)\n        xbar = tl.where(mask, x - mean[:, None], 0.0)\n        var = tl.sum(xbar * xbar, axis=1) / N\n    else:\n        xbar = tl.where(mask, x, 0.0)\n        var = tl.sum(xbar * xbar, axis=1) / N\n        mean = 0.0\n    rstd = tl.rsqrt(var + eps)\n    rstd_offsets = group * M + rows\n    rstd_mask = rows < M\n    tl.store(Rstd + rstd_offsets, rstd, mask=rstd_mask)\n    w_offsets = cols + group * N\n    w_mask = cols < N\n    w = tl.load(W + w_offsets, mask=w_mask, other=0.0).to(tl.float32)\n    if HAS_BIAS:\n        b = tl.load(B + w_offsets, mask=w_mask, other=0.0).to(tl.float32)\n    if not IS_RMS_NORM:\n        x_hat = (x - mean[:, None]) * rstd[:, None]\n    else:\n        x_hat = x * rstd[:, None]\n    y = x_hat * w[None, :] + b[None, :] if HAS_BIAS else x_hat * w[None, :]\n    if HAS_Z and NORM_BEFORE_GATE:\n        Z_base = Z + rows[:, None] * stride_z_row + col_offsets\n        z = tl.load(Z_base, mask=mask, other=0.0).to(tl.float32)\n        if ACTIVATION == 'swish' or ACTIVATION == 'silu':\n            y *= z * tl.sigmoid(z)\n        elif ACTIVATION == 'sigmoid':\n            y *= tl.sigmoid(z)\n    tl.store(Y_base, y, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/layernorm_guard.py"
    },
    {
        "id": "chunk_gated_delta_rule_fwd_kernel_h_blockdim64",
        "coords": [
            5,
            7,
            20
        ],
        "fiber": 1,
        "logic": "@triton.heuristics({'USE_G': lambda args: args['g'] is not None, 'USE_GK': lambda args: args['gk'] is not None, 'USE_INITIAL_STATE': lambda args: args['h0'] is not None, 'STORE_FINAL_STATE': lambda args: args['ht'] is not None, 'SAVE_NEW_VALUE': lambda args: args['v_new'] is not None, 'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({'BV': BV}, num_warps=num_warps, num_stages=num_stages) for num_warps in [2, 4] for num_stages in [2, 3, 4] for BV in [32, 64]], key=['H', 'K', 'V', 'BT'], use_cuda_graph=use_cuda_graph)\n@triton.jit(do_not_specialize=['T'])\ndef chunk_gated_delta_rule_fwd_kernel_h_blockdim64(k, v, w, v_new, g, gk, h, h0, ht, cu_seqlens, chunk_offsets, T, H: tl.constexpr, Hg: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BV: tl.constexpr, USE_G: tl.constexpr, USE_GK: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, STORE_FINAL_STATE: tl.constexpr, SAVE_NEW_VALUE: tl.constexpr, IS_VARLEN: tl.constexpr):\n    i_v, i_nh = (tl.program_id(0), tl.program_id(1))\n    i_n, i_h = (i_nh // H, i_nh % H)\n    if IS_VARLEN:\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n        NT = tl.cdiv(T, BT)\n        boh = tl.load(chunk_offsets + i_n).to(tl.int32)\n    else:\n        bos, eos = (i_n * T, i_n * T + T)\n        NT = tl.cdiv(T, BT)\n        boh = i_n * NT\n    b_h1 = tl.zeros([BV, 64], dtype=tl.float32)\n    if K > 64:\n        b_h2 = tl.zeros([BV, 64], dtype=tl.float32)\n    if K > 128:\n        b_h3 = tl.zeros([BV, 64], dtype=tl.float32)\n    if K > 192:\n        b_h4 = tl.zeros([BV, 64], dtype=tl.float32)\n    h += ((boh * H + i_h) * V * K).to(tl.int64)\n    v += ((bos * H + i_h) * V).to(tl.int64)\n    k += ((bos * Hg + i_h // (H // Hg)) * K).to(tl.int64)\n    w += ((bos * H + i_h) * K).to(tl.int64)\n    if SAVE_NEW_VALUE:\n        v_new += ((bos * H + i_h) * V).to(tl.int64)\n    stride_v = H * V\n    stride_h = H * V * K\n    stride_k = Hg * K\n    stride_w = H * K\n    if USE_INITIAL_STATE:\n        h0 = h0 + i_nh * V * K\n    if STORE_FINAL_STATE:\n        ht = ht + i_nh * V * K\n    if USE_INITIAL_STATE:\n        p_h0_1 = tl.make_block_ptr(h0, (V, K), (K, 1), (i_v * BV, 0), (BV, 64), (1, 0))\n        b_h1 += tl.load(p_h0_1, boundary_check=(0, 1)).to(tl.float32)\n        if K > 64:\n            p_h0_2 = tl.make_block_ptr(h0, (V, K), (K, 1), (i_v * BV, 64), (BV, 64), (1, 0))\n            b_h2 += tl.load(p_h0_2, boundary_check=(0, 1)).to(tl.float32)\n        if K > 128:\n            p_h0_3 = tl.make_block_ptr(h0, (V, K), (K, 1), (i_v * BV, 128), (BV, 64), (1, 0))\n            b_h3 += tl.load(p_h0_3, boundary_check=(0, 1)).to(tl.float32)\n        if K > 192:\n            p_h0_4 = tl.make_block_ptr(h0, (V, K), (K, 1), (i_v * BV, 192), (BV, 64), (1, 0))\n            b_h4 += tl.load(p_h0_4, boundary_check=(0, 1)).to(tl.float32)\n    for i_t in range(NT):\n        p_h1 = tl.make_block_ptr(h + i_t * stride_h, (V, K), (K, 1), (i_v * BV, 0), (BV, 64), (1, 0))\n        tl.store(p_h1, b_h1.to(p_h1.dtype.element_ty), boundary_check=(0, 1))\n        if K > 64:\n            p_h2 = tl.make_block_ptr(h + i_t * stride_h, (V, K), (K, 1), (i_v * BV, 64), (BV, 64), (1, 0))\n            tl.store(p_h2, b_h2.to(p_h2.dtype.element_ty), boundary_check=(0, 1))\n        if K > 128:\n            p_h3 = tl.make_block_ptr(h + i_t * stride_h, (V, K), (K, 1), (i_v * BV, 128), (BV, 64), (1, 0))\n            tl.store(p_h3, b_h3.to(p_h3.dtype.element_ty), boundary_check=(0, 1))\n        if K > 192:\n            p_h4 = tl.make_block_ptr(h + i_t * stride_h, (V, K), (K, 1), (i_v * BV, 192), (BV, 64), (1, 0))\n            tl.store(p_h4, b_h4.to(p_h4.dtype.element_ty), boundary_check=(0, 1))\n        p_w = tl.make_block_ptr(w, (T, K), (stride_w, 1), (i_t * BT, 0), (BT, 64), (1, 0))\n        b_w = tl.load(p_w, boundary_check=(0, 1))\n        b_v = tl.dot(b_w, tl.trans(b_h1).to(b_w.dtype))\n        if K > 64:\n            p_w = tl.make_block_ptr(w, (T, K), (stride_w, 1), (i_t * BT, 64), (BT, 64), (1, 0))\n            b_w = tl.load(p_w, boundary_check=(0, 1))\n            b_v += tl.dot(b_w, tl.trans(b_h2).to(b_w.dtype))\n        if K > 128:\n            p_w = tl.make_block_ptr(w, (T, K), (stride_w, 1), (i_t * BT, 128), (BT, 64), (1, 0))\n            b_w = tl.load(p_w, boundary_check=(0, 1))\n            b_v += tl.dot(b_w, tl.trans(b_h3).to(b_w.dtype))\n        if K > 192:\n            p_w = tl.make_block_ptr(w, (T, K), (stride_w, 1), (i_t * BT, 192), (BT, 64), (1, 0))\n            b_w = tl.load(p_w, boundary_check=(0, 1))\n            b_v += tl.dot(b_w, tl.trans(b_h4).to(b_w.dtype))\n        p_v = tl.make_block_ptr(v, (T, V), (stride_v, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n        b_v = tl.load(p_v, boundary_check=(0, 1)) - b_v\n        if SAVE_NEW_VALUE:\n            p_v = tl.make_block_ptr(v_new, (T, V), (stride_v, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n            tl.store(p_v, b_v.to(p_v.dtype.element_ty), boundary_check=(0, 1))\n        last_idx = min((i_t + 1) * BT, T) - 1\n        if USE_G:\n            m_t = i_t * BT + tl.arange(0, BT) < T\n            b_g_last = tl.load(g + bos * H + last_idx * H + i_h)\n            p_g = tl.make_block_ptr(g + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n            b_g = tl.load(p_g, boundary_check=(0,))\n            b_v = b_v * tl.where(m_t, exp(b_g_last - b_g), 0)[:, None]\n            b_g_last = exp(b_g_last)\n            b_h1 *= b_g_last\n            if K > 64:\n                b_h2 *= b_g_last\n            if K > 128:\n                b_h3 *= b_g_last\n            if K > 192:\n                b_h4 *= b_g_last\n        if USE_GK:\n            o_k1 = tl.arange(0, 64)\n            b_gk_last1 = tl.load(gk + (bos + last_idx) * H * K + i_h * K + o_k1, mask=o_k1 < K, other=0.0)\n            b_h1 *= exp(b_gk_last1)[None, :]\n            if K > 64:\n                o_k2 = 64 + o_k1\n                b_gk_last2 = tl.load(gk + (bos + last_idx) * H * K + i_h * K + o_k2, mask=o_k2 < K, other=0.0)\n                b_h2 *= exp(b_gk_last2)[None, :]\n            if K > 128:\n                o_k3 = 128 + o_k1\n                b_gk_last3 = tl.load(gk + (bos + last_idx) * H * K + i_h * K + o_k3, mask=o_k3 < K, other=0.0)\n                b_h3 *= exp(b_gk_last3)[None, :]\n            if K > 192:\n                o_k4 = 192 + o_k1\n                b_gk_last4 = tl.load(gk + (bos + last_idx) * H * K + i_h * K + o_k4, mask=o_k4 < K, other=0.0)\n                b_h4 *= exp(b_gk_last4)[None, :]\n        b_v = b_v.to(k.dtype.element_ty)\n        p_k = tl.make_block_ptr(k, (K, T), (1, stride_k), (0, i_t * BT), (64, BT), (0, 1))\n        b_k = tl.load(p_k, boundary_check=(0, 1))\n        b_h1 += tl.trans(tl.dot(b_k, b_v))\n        if K > 64:\n            p_k = tl.make_block_ptr(k, (K, T), (1, stride_k), (64, i_t * BT), (64, BT), (0, 1))\n            b_k = tl.load(p_k, boundary_check=(0, 1))\n            b_h2 += tl.trans(tl.dot(b_k, b_v))\n        if K > 128:\n            p_k = tl.make_block_ptr(k, (K, T), (1, stride_k), (128, i_t * BT), (64, BT), (0, 1))\n            b_k = tl.load(p_k, boundary_check=(0, 1))\n            b_h3 += tl.trans(tl.dot(b_k, b_v))\n        if K > 192:\n            p_k = tl.make_block_ptr(k, (K, T), (1, stride_k), (192, i_t * BT), (64, BT), (0, 1))\n            b_k = tl.load(p_k, boundary_check=(0, 1))\n            b_h4 += tl.trans(tl.dot(b_k, b_v))\n    if STORE_FINAL_STATE:\n        p_ht = tl.make_block_ptr(ht, (V, K), (K, 1), (i_v * BV, 0), (BV, 64), (1, 0))\n        tl.store(p_ht, b_h1.to(p_ht.dtype.element_ty), boundary_check=(0, 1))\n        if K > 64:\n            p_ht = tl.make_block_ptr(ht, (V, K), (K, 1), (i_v * BV, 64), (BV, 64), (1, 0))\n            tl.store(p_ht, b_h2.to(p_ht.dtype.element_ty), boundary_check=(0, 1))\n        if K > 128:\n            p_ht = tl.make_block_ptr(ht, (V, K), (K, 1), (i_v * BV, 128), (BV, 64), (1, 0))\n            tl.store(p_ht, b_h3.to(p_ht.dtype.element_ty), boundary_check=(0, 1))\n        if K > 192:\n            p_ht = tl.make_block_ptr(ht, (V, K), (K, 1), (i_v * BV, 192), (BV, 64), (1, 0))\n            tl.store(p_ht, b_h4.to(p_ht.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/chunk_delta_h.py"
    },
    {
        "id": "layer_norm_gated_fwd_kernel",
        "coords": [
            16,
            25,
            18
        ],
        "fiber": 28,
        "logic": "@triton.heuristics({'STORE_RESIDUAL_OUT': lambda args: args['residual_out'] is not None, 'HAS_RESIDUAL': lambda args: args['residual'] is not None, 'HAS_WEIGHT': lambda args: args['w'] is not None, 'HAS_BIAS': lambda args: args['b'] is not None})\n@triton.jit\ndef layer_norm_gated_fwd_kernel(x, g, y, w, b, residual, residual_out, mean, rstd, eps, T, D: tl.constexpr, BT: tl.constexpr, BD: tl.constexpr, ACTIVATION: tl.constexpr, IS_RMS_NORM: tl.constexpr, STORE_RESIDUAL_OUT: tl.constexpr, HAS_RESIDUAL: tl.constexpr, HAS_WEIGHT: tl.constexpr, HAS_BIAS: tl.constexpr):\n    i_t = tl.program_id(0)\n    o_d = tl.arange(0, BD)\n    m_d = o_d < D\n    p_x = tl.make_block_ptr(x, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n    b_x = tl.load(p_x, boundary_check=(0, 1)).to(tl.float32)\n    if HAS_RESIDUAL:\n        p_res = tl.make_block_ptr(residual, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n        b_x += tl.load(p_res, boundary_check=(0, 1)).to(tl.float32)\n    if STORE_RESIDUAL_OUT:\n        p_res_out = tl.make_block_ptr(residual_out, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n        tl.store(p_res_out, b_x.to(p_res_out.dtype.element_ty), boundary_check=(0, 1))\n    if not IS_RMS_NORM:\n        b_mean = tl.sum(b_x, axis=1) / D\n        p_mean = tl.make_block_ptr(mean, (T,), (1,), (i_t * BT,), (BT,), (0,))\n        tl.store(p_mean, b_mean.to(p_mean.dtype.element_ty), boundary_check=(0,))\n        b_xbar = tl.where(m_d[None, :], b_x - b_mean[:, None], 0.0)\n        b_var = tl.sum(b_xbar * b_xbar, axis=1) / D\n    else:\n        b_xbar = tl.where(m_d[None, :], b_x, 0.0)\n        b_var = tl.sum(b_xbar * b_xbar, axis=1) / D\n    b_rstd = 1 / tl.sqrt(b_var + eps)\n    p_rstd = tl.make_block_ptr(rstd, (T,), (1,), (i_t * BT,), (BT,), (0,))\n    tl.store(p_rstd, b_rstd.to(p_rstd.dtype.element_ty), boundary_check=(0,))\n    if HAS_WEIGHT:\n        b_w = tl.load(w + o_d, mask=m_d).to(tl.float32)\n    if HAS_BIAS:\n        b_b = tl.load(b + o_d, mask=m_d).to(tl.float32)\n    b_x_hat = (b_x - b_mean[:, None]) * b_rstd[:, None] if not IS_RMS_NORM else b_x * b_rstd[:, None]\n    b_y = b_x_hat * b_w[None, :] if HAS_WEIGHT else b_x_hat\n    if HAS_BIAS:\n        b_y = b_y + b_b[None, :]\n    p_g = tl.make_block_ptr(g, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n    b_g = tl.load(p_g, boundary_check=(0, 1)).to(tl.float32)\n    if ACTIVATION == 'swish' or ACTIVATION == 'silu':\n        b_y = b_y * b_g * tl.sigmoid(b_g)\n    elif ACTIVATION == 'sigmoid':\n        b_y = b_y * tl.sigmoid(b_g)\n    p_y = tl.make_block_ptr(y, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n    tl.store(p_y, b_y.to(p_y.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "layer_norm_gated_fwd_kernel1",
        "coords": [
            15,
            15,
            16
        ],
        "fiber": 15,
        "logic": "@triton.heuristics({'STORE_RESIDUAL_OUT': lambda args: args['residual_out'] is not None, 'HAS_RESIDUAL': lambda args: args['residual'] is not None, 'HAS_WEIGHT': lambda args: args['w'] is not None, 'HAS_BIAS': lambda args: args['b'] is not None})\n@triton.jit\ndef layer_norm_gated_fwd_kernel1(x, g, y, w, b, residual, residual_out, mean, rstd, eps, D: tl.constexpr, BD: tl.constexpr, ACTIVATION: tl.constexpr, IS_RMS_NORM: tl.constexpr, STORE_RESIDUAL_OUT: tl.constexpr, HAS_RESIDUAL: tl.constexpr, HAS_WEIGHT: tl.constexpr, HAS_BIAS: tl.constexpr):\n    i_t = tl.program_id(0)\n    x += i_t * D\n    y += i_t * D\n    g += i_t * D\n    if HAS_RESIDUAL:\n        residual += i_t * D\n    if STORE_RESIDUAL_OUT:\n        residual_out += i_t * D\n    o_d = tl.arange(0, BD)\n    m_d = o_d < D\n    b_x = tl.load(x + o_d, mask=m_d, other=0.0).to(tl.float32)\n    if HAS_RESIDUAL:\n        b_x += tl.load(residual + o_d, mask=m_d, other=0.0).to(tl.float32)\n    if STORE_RESIDUAL_OUT:\n        tl.store(residual_out + o_d, b_x, mask=m_d)\n    if not IS_RMS_NORM:\n        b_mean = tl.sum(b_x, axis=0) / D\n        tl.store(mean + i_t, b_mean)\n        b_xbar = tl.where(m_d, b_x - b_mean, 0.0)\n        b_var = tl.sum(b_xbar * b_xbar, axis=0) / D\n    else:\n        b_xbar = tl.where(m_d, b_x, 0.0)\n        b_var = tl.sum(b_xbar * b_xbar, axis=0) / D\n    b_rstd = 1 / tl.sqrt(b_var + eps)\n    tl.store(rstd + i_t, b_rstd)\n    if HAS_WEIGHT:\n        b_w = tl.load(w + o_d, mask=m_d).to(tl.float32)\n    if HAS_BIAS:\n        b_b = tl.load(b + o_d, mask=m_d).to(tl.float32)\n    b_x_hat = (b_x - b_mean) * b_rstd if not IS_RMS_NORM else b_x * b_rstd\n    b_y = b_x_hat * b_w if HAS_WEIGHT else b_x_hat\n    if HAS_BIAS:\n        b_y = b_y + b_b\n    b_g = tl.load(g + o_d, mask=m_d, other=0.0).to(tl.float32)\n    if ACTIVATION == 'swish' or ACTIVATION == 'silu':\n        b_y = b_y * b_g * tl.sigmoid(b_g)\n    elif ACTIVATION == 'sigmoid':\n        b_y = b_y * tl.sigmoid(b_g)\n    tl.store(y + o_d, b_y, mask=m_d)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "chunk_kda_scaled_dot_kkt_fwd_kernel_intra_sub_inter",
        "coords": [
            23,
            27,
            22
        ],
        "fiber": 10,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({'BK': BK}, num_warps=num_warps, num_stages=num_stages) for BK in [32, 64] for num_warps in [1, 2, 4, 8] for num_stages in [2, 3, 4]], key=['BC'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_kda_scaled_dot_kkt_fwd_kernel_intra_sub_inter(q, k, g, beta, A, Aqk, scale, cu_seqlens, chunk_indices, T, H: tl.constexpr, K: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, BK: tl.constexpr, NC: tl.constexpr, IS_VARLEN: tl.constexpr):\n    i_t, i_c, i_bh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    i_i, i_j = (i_c // NC, i_c % NC)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    if i_t * BT + i_i * BC >= T:\n        return\n    if i_i <= i_j:\n        return\n    q += (bos * H + i_h) * K\n    k += (bos * H + i_h) * K\n    g += (bos * H + i_h) * K\n    A += (bos * H + i_h) * BT\n    Aqk += (bos * H + i_h) * BT\n    p_b = tl.make_block_ptr(beta + bos * H + i_h, (T,), (H,), (i_t * BT + i_i * BC,), (BC,), (0,))\n    b_b = tl.load(p_b, boundary_check=(0,))\n    b_A = tl.zeros([BC, BC], dtype=tl.float32)\n    b_Aqk = tl.zeros([BC, BC], dtype=tl.float32)\n    for i_k in range(tl.cdiv(K, BK)):\n        p_q = tl.make_block_ptr(q, (T, K), (H * K, 1), (i_t * BT + i_i * BC, i_k * BK), (BC, BK), (1, 0))\n        p_k = tl.make_block_ptr(k, (T, K), (H * K, 1), (i_t * BT + i_i * BC, i_k * BK), (BC, BK), (1, 0))\n        p_g = tl.make_block_ptr(g, (T, K), (H * K, 1), (i_t * BT + i_i * BC, i_k * BK), (BC, BK), (1, 0))\n        b_kt = tl.make_block_ptr(k, (K, T), (1, H * K), (i_k * BK, i_t * BT + i_j * BC), (BK, BC), (0, 1))\n        p_gk = tl.make_block_ptr(g, (K, T), (1, H * K), (i_k * BK, i_t * BT + i_j * BC), (BK, BC), (0, 1))\n        o_k = i_k * BK + tl.arange(0, BK)\n        m_k = o_k < K\n        b_gn = tl.load(g + (i_t * BT + i_i * BC) * H * K + o_k, mask=m_k, other=0)\n        b_g = tl.load(p_g, boundary_check=(0, 1))\n        b_k = tl.load(p_k, boundary_check=(0, 1)) * exp(b_g - b_gn[None, :])\n        b_gk = tl.load(p_gk, boundary_check=(0, 1))\n        b_kt = tl.load(b_kt, boundary_check=(0, 1))\n        b_ktg = b_kt * exp(b_gn[:, None] - b_gk)\n        b_A += tl.dot(b_k, b_ktg)\n        b_q = tl.load(p_q, boundary_check=(0, 1))\n        b_qg = b_q * exp(b_g - b_gn[None, :]) * scale\n        b_Aqk += tl.dot(b_qg, b_ktg)\n    b_A *= b_b[:, None]\n    p_A = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + i_i * BC, i_j * BC), (BC, BC), (1, 0))\n    tl.store(p_A, b_A.to(A.dtype.element_ty), boundary_check=(0, 1))\n    p_Aqk = tl.make_block_ptr(Aqk, (T, BT), (H * BT, 1), (i_t * BT + i_i * BC, i_j * BC), (BC, BC), (1, 0))\n    tl.store(p_Aqk, b_Aqk.to(Aqk.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "chunk_kda_scaled_dot_kkt_fwd_kernel_intra_sub_intra",
        "coords": [
            30,
            15,
            28
        ],
        "fiber": 11,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps) for num_warps in [1, 2, 4, 8]], key=['BK', 'BT'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_kda_scaled_dot_kkt_fwd_kernel_intra_sub_intra(q, k, g, beta, A, Aqk, scale, cu_seqlens, chunk_indices, T, H: tl.constexpr, K: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, BK: tl.constexpr, IS_VARLEN: tl.constexpr):\n    i_t, i_i, i_bh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    if i_t * BT + i_i * BC >= T:\n        return\n    o_i = tl.arange(0, BC)\n    o_k = tl.arange(0, BK)\n    m_k = o_k < K\n    m_A = i_t * BT + i_i * BC + o_i < T\n    o_A = (bos + i_t * BT + i_i * BC + o_i) * H * BT + i_h * BT + i_i * BC\n    p_q = tl.make_block_ptr(q + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT + i_i * BC, 0), (BC, BK), (1, 0))\n    p_k = tl.make_block_ptr(k + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT + i_i * BC, 0), (BC, BK), (1, 0))\n    p_g = tl.make_block_ptr(g + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT + i_i * BC, 0), (BC, BK), (1, 0))\n    b_q = tl.load(p_q, boundary_check=(0, 1))\n    b_k = tl.load(p_k, boundary_check=(0, 1))\n    b_g = tl.load(p_g, boundary_check=(0, 1))\n    p_b = beta + (bos + i_t * BT + i_i * BC + o_i) * H + i_h\n    b_k = b_k * tl.load(p_b, mask=m_A, other=0)[:, None]\n    p_kt = k + (bos + i_t * BT + i_i * BC) * H * K + i_h * K + o_k\n    p_gk = g + (bos + i_t * BT + i_i * BC) * H * K + i_h * K + o_k\n    for j in range(0, min(BC, T - i_t * BT - i_i * BC)):\n        b_kt = tl.load(p_kt, mask=m_k, other=0).to(tl.float32)\n        b_gk = tl.load(p_gk, mask=m_k, other=0).to(tl.float32)\n        b_ktg = b_kt[None, :] * exp(b_g - b_gk[None, :])\n        b_A = tl.sum(b_k * b_ktg, 1)\n        b_A = tl.where(o_i > j, b_A, 0.0)\n        b_Aqk = tl.sum(b_q * b_ktg, 1)\n        b_Aqk = tl.where(o_i >= j, b_Aqk * scale, 0.0)\n        tl.store(A + o_A + j, b_A, mask=m_A)\n        tl.store(Aqk + o_A + j, b_Aqk, mask=m_A)\n        p_kt += H * K\n        p_gk += H * K",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "recompute_w_u_fwd_kernel",
        "coords": [
            11,
            11,
            29
        ],
        "fiber": 20,
        "logic": "@triton.heuristics({'STORE_QG': lambda args: args['qg'] is not None, 'STORE_KG': lambda args: args['kg'] is not None, 'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps, num_stages=num_stages) for num_warps in [2, 4, 8] for num_stages in [2, 3, 4]], key=['H', 'K', 'V', 'BT', 'BK', 'BV', 'IS_VARLEN'])\n@triton.jit(do_not_specialize=['T'])\ndef recompute_w_u_fwd_kernel(q, k, qg, kg, v, beta, w, u, A, gk, cu_seqlens, chunk_indices, T, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, STORE_QG: tl.constexpr, STORE_KG: tl.constexpr, IS_VARLEN: tl.constexpr, DOT_PRECISION: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    p_b = tl.make_block_ptr(beta + bos * H + i_h, (T,), (H,), (i_t * BT,), (BT,), (0,))\n    b_b = tl.load(p_b, boundary_check=(0,))\n    p_A = tl.make_block_ptr(A + (bos * H + i_h) * BT, (T, BT), (H * BT, 1), (i_t * BT, 0), (BT, BT), (1, 0))\n    b_A = tl.load(p_A, boundary_check=(0, 1))\n    for i_v in range(tl.cdiv(V, BV)):\n        p_v = tl.make_block_ptr(v + (bos * H + i_h) * V, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n        p_u = tl.make_block_ptr(u + (bos * H + i_h) * V, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n        b_v = tl.load(p_v, boundary_check=(0, 1))\n        b_vb = (b_v * b_b[:, None]).to(b_v.dtype)\n        b_u = tl.dot(b_A, b_vb, input_precision=DOT_PRECISION)\n        tl.store(p_u, b_u.to(p_u.dtype.element_ty), boundary_check=(0, 1))\n    for i_k in range(tl.cdiv(K, BK)):\n        p_w = tl.make_block_ptr(w + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        p_k = tl.make_block_ptr(k + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        b_k = tl.load(p_k, boundary_check=(0, 1))\n        b_kb = b_k * b_b[:, None]\n        p_gk = tl.make_block_ptr(gk + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        b_gk = tl.load(p_gk, boundary_check=(0, 1))\n        b_kb *= exp(b_gk)\n        if STORE_QG:\n            p_q = tl.make_block_ptr(q + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n            p_qg = tl.make_block_ptr(qg + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n            b_q = tl.load(p_q, boundary_check=(0, 1))\n            b_qg = b_q * exp(b_gk)\n            tl.store(p_qg, b_qg.to(p_qg.dtype.element_ty), boundary_check=(0, 1))\n        if STORE_KG:\n            last_idx = min(i_t * BT + BT, T) - 1\n            o_k = i_k * BK + tl.arange(0, BK)\n            m_k = o_k < K\n            b_gn = tl.load(gk + ((bos + last_idx) * H + i_h) * K + o_k, mask=m_k, other=0.0)\n            b_kg = b_k * exp(b_gn - b_gk)\n            p_kg = tl.make_block_ptr(kg + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n            tl.store(p_kg, b_kg.to(p_kg.dtype.element_ty), boundary_check=(0, 1))\n        b_w = tl.dot(b_A, b_kb.to(b_k.dtype))\n        tl.store(p_w, b_w.to(p_w.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "chunk_gla_fwd_kernel_o",
        "coords": [
            26,
            6,
            17
        ],
        "fiber": 18,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({'BK': BK, 'BV': BV}, num_warps=num_warps, num_stages=num_stages) for BK in [32, 64] for BV in [64, 128] for num_warps in [2, 4, 8] for num_stages in [2, 3, 4]], key=['BT'])\n@triton.jit(do_not_specialize=['T'])\ndef chunk_gla_fwd_kernel_o(q, v, g, h, o, A, cu_seqlens, chunk_indices, scale, T, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, IS_VARLEN: tl.constexpr):\n    i_v, i_t, i_bh = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_tg = i_t\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n        NT = tl.cdiv(T, BT)\n    else:\n        NT = tl.cdiv(T, BT)\n        i_tg = i_b * NT + i_t\n        bos, eos = (i_b * T, i_b * T + T)\n    m_s = tl.arange(0, BT)[:, None] >= tl.arange(0, BT)[None, :]\n    b_o = tl.zeros([BT, BV], dtype=tl.float32)\n    for i_k in range(tl.cdiv(K, BK)):\n        p_q = tl.make_block_ptr(q + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        p_g = tl.make_block_ptr(g + (bos * H + i_h) * K, (T, K), (H * K, 1), (i_t * BT, i_k * BK), (BT, BK), (1, 0))\n        p_h = tl.make_block_ptr(h + (i_tg * H + i_h) * K * V, (K, V), (V, 1), (i_k * BK, i_v * BV), (BK, BV), (1, 0))\n        b_q = tl.load(p_q, boundary_check=(0, 1))\n        b_q = (b_q * scale).to(b_q.dtype)\n        b_g = tl.load(p_g, boundary_check=(0, 1))\n        b_qg = (b_q * exp(b_g)).to(b_q.dtype)\n        b_h = tl.load(p_h, boundary_check=(0, 1))\n        if i_k >= 0:\n            b_o += tl.dot(b_qg, b_h.to(b_qg.dtype))\n    p_v = tl.make_block_ptr(v + (bos * H + i_h) * V, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n    p_o = tl.make_block_ptr(o + (bos * H + i_h) * V, (T, V), (H * V, 1), (i_t * BT, i_v * BV), (BT, BV), (1, 0))\n    p_A = tl.make_block_ptr(A + (bos * H + i_h) * BT, (T, BT), (H * BT, 1), (i_t * BT, 0), (BT, BT), (1, 0))\n    b_v = tl.load(p_v, boundary_check=(0, 1))\n    b_A = tl.load(p_A, boundary_check=(0, 1))\n    b_A = tl.where(m_s, b_A, 0.0).to(b_v.dtype)\n    b_o += tl.dot(b_A, b_v, allow_tf32=False)\n    tl.store(p_o, b_o.to(p_o.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "kda_gate_fwd_kernel",
        "coords": [
            11,
            5,
            13
        ],
        "fiber": 29,
        "logic": "@triton.autotune(configs=[triton.Config({'BT': bt}, num_warps=nw, num_stages=ns) for bt in BT_LIST_AUTOTUNE for nw in NUM_WARPS_AUTOTUNE for ns in [2, 3]], key=['H', 'D'])\n@triton.jit\ndef kda_gate_fwd_kernel(g, A, y, g_bias, beta: tl.constexpr, threshold: tl.constexpr, T, H, D: tl.constexpr, BT: tl.constexpr, BD: tl.constexpr, HAS_BIAS: tl.constexpr):\n    i_t, i_h = (tl.program_id(0), tl.program_id(1))\n    n_t = i_t * BT\n    b_a = tl.load(A + i_h).to(tl.float32)\n    b_a = -tl.exp(b_a)\n    stride_row = H * D\n    stride_col = 1\n    g_ptr = tl.make_block_ptr(base=g + i_h * D, shape=(T, D), strides=(stride_row, stride_col), offsets=(n_t, 0), block_shape=(BT, BD), order=(1, 0))\n    y_ptr = tl.make_block_ptr(base=y + i_h * D, shape=(T, D), strides=(stride_row, stride_col), offsets=(n_t, 0), block_shape=(BT, BD), order=(1, 0))\n    b_g = tl.load(g_ptr, boundary_check=(0, 1)).to(tl.float32)\n    if HAS_BIAS:\n        n_d = tl.arange(0, BD)\n        bias_mask = n_d < D\n        b_bias = tl.load(g_bias + i_h * D + n_d, mask=bias_mask, other=0.0).to(tl.float32)\n        b_g = b_g + b_bias[None, :]\n    g_scaled = b_g * beta\n    use_linear = g_scaled > threshold\n    sp = tl.where(use_linear, b_g, 1.0 / beta * log(1.0 + tl.exp(g_scaled)))\n    b_y = b_a * sp\n    tl.store(y_ptr, b_y.to(y.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/kda.py"
    },
    {
        "id": "l2norm_fwd_kernel1",
        "coords": [
            8,
            1,
            16
        ],
        "fiber": 25,
        "logic": "@triton.autotune(configs=[triton.Config({}, num_warps=num_warps) for num_warps in [1, 2, 4, 8, 16, 32]], key=['D'])\n@triton.jit\ndef l2norm_fwd_kernel1(x, y, D, BD: tl.constexpr, eps):\n    i_t = tl.program_id(0)\n    x += i_t * D\n    y += i_t * D\n    cols = tl.arange(0, BD)\n    mask = cols < D\n    b_x = tl.load(x + cols, mask=mask, other=0.0).to(tl.float32)\n    b_var = tl.sum(b_x * b_x, axis=0)\n    b_rstd = 1 / tl.sqrt(b_var + eps)\n    b_y = b_x * b_rstd\n    tl.store(y + cols, b_y, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/l2norm.py"
    },
    {
        "id": "l2norm_fwd_kernel",
        "coords": [
            21,
            2,
            9
        ],
        "fiber": 1,
        "logic": "@triton.autotune(configs=[triton.Config({'BT': BT}, num_warps=num_warps) for num_warps in [1, 2, 4, 8, 16] for BT in BT_LIST], key=['D'])\n@triton.jit(do_not_specialize=['NB'])\ndef l2norm_fwd_kernel(x, y, eps, NB, T, D: tl.constexpr, BT: tl.constexpr, BD: tl.constexpr):\n    i_t = tl.program_id(0)\n    p_x = tl.make_block_ptr(x, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n    b_x = tl.load(p_x, boundary_check=(0, 1)).to(tl.float32)\n    b_var = tl.sum(b_x * b_x, axis=1)\n    b_y = b_x / tl.sqrt(b_var + eps)[:, None]\n    p_y = tl.make_block_ptr(y, (T, D), (D, 1), (i_t * BT, 0), (BT, BD), (1, 0))\n    tl.store(p_y, b_y.to(p_y.dtype.element_ty), boundary_check=(0, 1))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/l2norm.py"
    },
    {
        "id": "l2norm_fwd_kernel2",
        "coords": [
            28,
            14,
            3
        ],
        "fiber": 14,
        "logic": "@triton.jit\ndef l2norm_fwd_kernel2(X, Y, eps, M, N: tl.constexpr, BD: tl.constexpr, MBLOCK: tl.constexpr):\n    xoffset = tl.program_id(0) * MBLOCK\n    row_idx = xoffset + tl.arange(0, MBLOCK)[:, None]\n    xmask = row_idx < M\n    rindex = tl.arange(0, BD)[None, :]\n    cmask = rindex < N\n    mask = xmask & cmask\n    xs = tl.load(X + (rindex + N * row_idx), mask, other=0.0).to(tl.float32)\n    square = tl.broadcast_to(xs * xs, [MBLOCK, BD])\n    square_sum = tl.sum(tl.where(xmask, square, 0), 1)[:, None]\n    rsqrt = tl.rsqrt(square_sum + eps)\n    tl.store(Y + (rindex + N * row_idx), xs * rsqrt, mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/l2norm.py"
    },
    {
        "id": "solve_tril_16x16_kernel",
        "coords": [
            0,
            5,
            28
        ],
        "fiber": 2,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps, num_stages=num_stages) for num_warps in [1, 2, 4, 8] for num_stages in [2, 3, 4, 5]], key=['BT'])\n@triton.jit(do_not_specialize=['T'])\ndef solve_tril_16x16_kernel(A, Ai, cu_seqlens, chunk_indices, T, H: tl.constexpr, BT: tl.constexpr, USE_TMA: tl.constexpr, IS_VARLEN: tl.constexpr, DOT_PRECISION: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    o_i = tl.arange(0, 16)\n    m_A = o_i[:, None] > o_i[None, :]\n    m_I = o_i[:, None] == o_i[None, :]\n    A = A + (bos * H + i_h) * BT\n    Ai = Ai + (bos * H + i_h) * 16\n    offset = i_t * 16 % BT\n    if not USE_TMA:\n        p_A = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * 16, offset), (16, 16), (1, 0))\n        b_A = tl.load(p_A, boundary_check=(0, 1)).to(tl.float32)\n    else:\n        desc = make_tensor_descriptor(A, [T, BT], [H * BT, 1], [16, 16])\n        desc_o = make_tensor_descriptor(Ai, [T, 16], [H * 16, 1], [16, 16])\n        b_A = desc.load([i_t * 16, offset]).to(tl.float32)\n    b_A = -tl.where(m_A, b_A, 0)\n    for i in range(2, min(16, T - i_t * 16)):\n        b_a = -tl.load(A + (i_t * 16 + i) * H * BT + o_i + offset)\n        b_a = b_a + tl.sum(b_a[:, None] * b_A, 0)\n        b_A = tl.where((o_i == i)[:, None], b_a, b_A)\n    b_A += m_I\n    if not USE_TMA:\n        p_Ai = tl.make_block_ptr(Ai, (T, 16), (H * 16, 1), (i_t * 16, 0), (16, 16), (1, 0))\n        tl.store(p_Ai, b_A.to(p_Ai.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n    else:\n        desc_o.store([i_t * 16, 0], b_A.to(desc_o.dtype, fp_downcast_rounding='rtne'))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/solve_tril.py"
    },
    {
        "id": "merge_16x16_to_32x32_inverse_kernel",
        "coords": [
            25,
            25,
            26
        ],
        "fiber": 14,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps, num_stages=num_stages) for num_warps in [1, 2, 4, 8] for num_stages in [2, 3, 4, 5]], key=['H', 'BT', 'IS_VARLEN'])\n@triton.jit(do_not_specialize=['T'])\ndef merge_16x16_to_32x32_inverse_kernel(A, Ai, cu_seqlens, chunk_indices, T, H: tl.constexpr, BT: tl.constexpr, USE_TMA: tl.constexpr, IS_VARLEN: tl.constexpr, DOT_PRECISION: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    o_i = tl.arange(0, 16)\n    m_A = o_i[:, None] > o_i[None, :]\n    m_I = o_i[:, None] == o_i[None, :]\n    A += (bos * H + i_h) * BT\n    Ai += (bos * H + i_h) * BT\n    if not USE_TMA:\n        p_A_11 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT, 0), (16, 16), (1, 0))\n        p_A_22 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 16, 16), (16, 16), (1, 0))\n        b_Ai_11 = tl.load(p_A_11, boundary_check=(0, 1)).to(tl.float32)\n        b_Ai_22 = tl.load(p_A_22, boundary_check=(0, 1)).to(tl.float32)\n    else:\n        desc = make_tensor_descriptor(A, [T, BT], [H * BT, 1], [16, 16])\n        desc_o = make_tensor_descriptor(Ai, [T, BT], [H * BT, 1], [16, 16])\n        b_Ai_11 = desc.load([i_t * BT + 0, 0]).to(tl.float32)\n        b_Ai_22 = desc.load([i_t * BT + 16, 16]).to(tl.float32)\n    b_Ai_11 = -tl.where(m_A, b_Ai_11, 0)\n    b_Ai_22 = -tl.where(m_A, b_Ai_22, 0)\n    for i in range(2, min(16, T - i_t * BT)):\n        b_a_11 = -tl.load(A + (i_t * BT + i) * H * BT + o_i)\n        b_a_11 += tl.sum(b_a_11[:, None] * b_Ai_11, 0)\n        b_Ai_11 = tl.where((o_i == i)[:, None], b_a_11, b_Ai_11)\n    for i in range(16 + 2, min(32, T - i_t * BT)):\n        b_a_22 = -tl.load(A + (i_t * BT + i) * H * BT + o_i + 16)\n        b_a_22 += tl.sum(b_a_22[:, None] * b_Ai_22, 0)\n        b_Ai_22 = tl.where((o_i == i - 16)[:, None], b_a_22, b_Ai_22)\n    b_Ai_11 += m_I\n    b_Ai_22 += m_I\n    if not USE_TMA:\n        p_A_21 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 16, 0), (16, 16), (1, 0))\n        b_A_21 = tl.load(p_A_21, boundary_check=(0, 1)).to(tl.float32)\n    else:\n        b_A_21 = desc.load([i_t * BT + 16, 0]).to(tl.float32)\n    b_Ai_21 = -tl.dot(tl.dot(b_Ai_22, b_A_21, input_precision=DOT_PRECISION), b_Ai_11, input_precision=DOT_PRECISION)\n    if not USE_TMA:\n        p_Ai_11 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT, 0), (16, 16), (1, 0))\n        p_Ai_21 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 16, 0), (16, 16), (1, 0))\n        p_Ai_22 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 16, 16), (16, 16), (1, 0))\n        tl.store(p_Ai_11, b_Ai_11.to(p_Ai_11.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_22, b_Ai_22.to(p_Ai_22.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_21, b_Ai_21.to(p_Ai_21.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n    else:\n        desc_o.store([i_t * BT + 0, 0], b_Ai_11.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 16, 0], b_Ai_21.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 16, 16], b_Ai_22.to(desc_o.dtype, fp_downcast_rounding='rtne'))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/solve_tril.py"
    },
    {
        "id": "merge_16x16_to_64x64_inverse_kernel",
        "coords": [
            5,
            21,
            14
        ],
        "fiber": 9,
        "logic": "@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens'] is not None})\n@triton.autotune(configs=[triton.Config({}, num_warps=num_warps, num_stages=num_stages) for num_warps in [2, 4, 8] for num_stages in [2, 3, 4, 5]], key=['H', 'BT', 'IS_VARLEN'])\n@triton.jit(do_not_specialize=['T'])\ndef merge_16x16_to_64x64_inverse_kernel(A, Ai, cu_seqlens, chunk_indices, T, H: tl.constexpr, BT: tl.constexpr, USE_TMA: tl.constexpr, IS_VARLEN: tl.constexpr, DOT_PRECISION: tl.constexpr):\n    i_t, i_bh = (tl.program_id(0), tl.program_id(1))\n    i_b, i_h = (i_bh // H, i_bh % H)\n    if IS_VARLEN:\n        i_n, i_t = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int32))\n        bos, eos = (tl.load(cu_seqlens + i_n).to(tl.int32), tl.load(cu_seqlens + i_n + 1).to(tl.int32))\n        T = eos - bos\n    else:\n        bos, eos = (i_b * T, i_b * T + T)\n    o_i = tl.arange(0, 16)\n    m_A = o_i[:, None] > o_i[None, :]\n    m_I = o_i[:, None] == o_i[None, :]\n    A += (bos * H + i_h) * BT\n    Ai += (bos * H + i_h) * BT\n    if not USE_TMA:\n        p_A_11 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT, 0), (16, 16), (1, 0))\n        p_A_22 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 16, 16), (16, 16), (1, 0))\n        p_A_33 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 32, 32), (16, 16), (1, 0))\n        p_A_44 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 48, 48), (16, 16), (1, 0))\n        b_Ai_11 = tl.load(p_A_11, boundary_check=(0, 1)).to(tl.float32)\n        b_Ai_22 = tl.load(p_A_22, boundary_check=(0, 1)).to(tl.float32)\n        b_Ai_33 = tl.load(p_A_33, boundary_check=(0, 1)).to(tl.float32)\n        b_Ai_44 = tl.load(p_A_44, boundary_check=(0, 1)).to(tl.float32)\n    else:\n        desc = make_tensor_descriptor(A, [T, BT], [H * BT, 1], [16, 16])\n        desc_o = make_tensor_descriptor(Ai, [T, BT], [H * BT, 1], [16, 16])\n        b_Ai_11 = desc.load([i_t * BT + 0, 0]).to(tl.float32)\n        b_Ai_22 = desc.load([i_t * BT + 16, 16]).to(tl.float32)\n        b_Ai_33 = desc.load([i_t * BT + 32, 32]).to(tl.float32)\n        b_Ai_44 = desc.load([i_t * BT + 48, 48]).to(tl.float32)\n    b_Ai_11 = -tl.where(m_A, b_Ai_11, 0)\n    b_Ai_22 = -tl.where(m_A, b_Ai_22, 0)\n    b_Ai_33 = -tl.where(m_A, b_Ai_33, 0)\n    b_Ai_44 = -tl.where(m_A, b_Ai_44, 0)\n    for i in range(2, min(16, T - i_t * BT)):\n        b_a_11 = -tl.load(A + (i_t * BT + i) * H * BT + o_i)\n        b_a_11 += tl.sum(b_a_11[:, None] * b_Ai_11, 0)\n        b_Ai_11 = tl.where((o_i == i)[:, None], b_a_11, b_Ai_11)\n    for i in range(16 + 2, min(32, T - i_t * BT)):\n        b_a_22 = -tl.load(A + (i_t * BT + i) * H * BT + o_i + 16)\n        b_a_22 += tl.sum(b_a_22[:, None] * b_Ai_22, 0)\n        b_Ai_22 = tl.where((o_i == i - 16)[:, None], b_a_22, b_Ai_22)\n    for i in range(32 + 2, min(48, T - i_t * BT)):\n        b_a_33 = -tl.load(A + (i_t * BT + i) * H * BT + o_i + 32)\n        b_a_33 += tl.sum(b_a_33[:, None] * b_Ai_33, 0)\n        b_Ai_33 = tl.where((o_i == i - 32)[:, None], b_a_33, b_Ai_33)\n    for i in range(48 + 2, min(64, T - i_t * BT)):\n        b_a_44 = -tl.load(A + (i_t * BT + i) * H * BT + o_i + 48)\n        b_a_44 += tl.sum(b_a_44[:, None] * b_Ai_44, 0)\n        b_Ai_44 = tl.where((o_i == i - 48)[:, None], b_a_44, b_Ai_44)\n    b_Ai_11 += m_I\n    b_Ai_22 += m_I\n    b_Ai_33 += m_I\n    b_Ai_44 += m_I\n    if not USE_TMA:\n        p_A_21 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 16, 0), (16, 16), (1, 0))\n        p_A_31 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 32, 0), (16, 16), (1, 0))\n        p_A_32 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 32, 16), (16, 16), (1, 0))\n        p_A_41 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 48, 0), (16, 16), (1, 0))\n        p_A_42 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 48, 16), (16, 16), (1, 0))\n        p_A_43 = tl.make_block_ptr(A, (T, BT), (H * BT, 1), (i_t * BT + 48, 32), (16, 16), (1, 0))\n        b_A_21 = tl.load(p_A_21, boundary_check=(0, 1)).to(tl.float32)\n        b_A_31 = tl.load(p_A_31, boundary_check=(0, 1)).to(tl.float32)\n        b_A_32 = tl.load(p_A_32, boundary_check=(0, 1)).to(tl.float32)\n        b_A_41 = tl.load(p_A_41, boundary_check=(0, 1)).to(tl.float32)\n        b_A_42 = tl.load(p_A_42, boundary_check=(0, 1)).to(tl.float32)\n        b_A_43 = tl.load(p_A_43, boundary_check=(0, 1)).to(tl.float32)\n    else:\n        b_A_21 = desc.load([i_t * BT + 16, 0]).to(tl.float32)\n        b_A_31 = desc.load([i_t * BT + 32, 0]).to(tl.float32)\n        b_A_32 = desc.load([i_t * BT + 32, 16]).to(tl.float32)\n        b_A_41 = desc.load([i_t * BT + 48, 0]).to(tl.float32)\n        b_A_42 = desc.load([i_t * BT + 48, 16]).to(tl.float32)\n        b_A_43 = desc.load([i_t * BT + 48, 32]).to(tl.float32)\n    b_Ai_21 = -tl.dot(tl.dot(b_Ai_22, b_A_21, input_precision=DOT_PRECISION), b_Ai_11, input_precision=DOT_PRECISION)\n    b_Ai_32 = -tl.dot(tl.dot(b_Ai_33, b_A_32, input_precision=DOT_PRECISION), b_Ai_22, input_precision=DOT_PRECISION)\n    b_Ai_43 = -tl.dot(tl.dot(b_Ai_44, b_A_43, input_precision=DOT_PRECISION), b_Ai_33, input_precision=DOT_PRECISION)\n    b_Ai_31 = -tl.dot(b_Ai_33, tl.dot(b_A_31, b_Ai_11, input_precision=DOT_PRECISION) + tl.dot(b_A_32, b_Ai_21, input_precision=DOT_PRECISION), input_precision=DOT_PRECISION)\n    b_Ai_42 = -tl.dot(b_Ai_44, tl.dot(b_A_42, b_Ai_22, input_precision=DOT_PRECISION) + tl.dot(b_A_43, b_Ai_32, input_precision=DOT_PRECISION), input_precision=DOT_PRECISION)\n    b_Ai_41 = -tl.dot(b_Ai_44, tl.dot(b_A_41, b_Ai_11, input_precision=DOT_PRECISION) + tl.dot(b_A_42, b_Ai_21, input_precision=DOT_PRECISION) + tl.dot(b_A_43, b_Ai_31, input_precision=DOT_PRECISION), input_precision=DOT_PRECISION)\n    if not USE_TMA:\n        p_Ai_11 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT, 0), (16, 16), (1, 0))\n        p_Ai_22 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 16, 16), (16, 16), (1, 0))\n        p_Ai_33 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 32, 32), (16, 16), (1, 0))\n        p_Ai_44 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 48, 48), (16, 16), (1, 0))\n        p_Ai_21 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 16, 0), (16, 16), (1, 0))\n        p_Ai_31 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 32, 0), (16, 16), (1, 0))\n        p_Ai_32 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 32, 16), (16, 16), (1, 0))\n        p_Ai_41 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 48, 0), (16, 16), (1, 0))\n        p_Ai_42 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 48, 16), (16, 16), (1, 0))\n        p_Ai_43 = tl.make_block_ptr(Ai, (T, BT), (H * BT, 1), (i_t * BT + 48, 32), (16, 16), (1, 0))\n        tl.store(p_Ai_11, b_Ai_11.to(p_Ai_11.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_22, b_Ai_22.to(p_Ai_22.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_33, b_Ai_33.to(p_Ai_33.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_44, b_Ai_44.to(p_Ai_44.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_21, b_Ai_21.to(p_Ai_21.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_31, b_Ai_31.to(p_Ai_31.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_32, b_Ai_32.to(p_Ai_32.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_41, b_Ai_41.to(p_Ai_41.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_42, b_Ai_42.to(p_Ai_42.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n        tl.store(p_Ai_43, b_Ai_43.to(p_Ai_43.dtype.element_ty, fp_downcast_rounding='rtne'), boundary_check=(0, 1))\n    else:\n        desc_o.store([i_t * BT + 0, 0], b_Ai_11.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 16, 16], b_Ai_22.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 32, 32], b_Ai_33.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 48, 48], b_Ai_44.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 16, 0], b_Ai_21.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 32, 0], b_Ai_31.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 32, 16], b_Ai_32.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 48, 0], b_Ai_41.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 48, 16], b_Ai_42.to(desc_o.dtype, fp_downcast_rounding='rtne'))\n        desc_o.store([i_t * BT + 48, 32], b_Ai_43.to(desc_o.dtype, fp_downcast_rounding='rtne'))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/solve_tril.py"
    },
    {
        "id": "_fused_post_conv_kernel",
        "coords": [
            8,
            8,
            23
        ],
        "fiber": 8,
        "logic": "@triton.jit\ndef _fused_post_conv_kernel(mixed_qkv_ptr, a_ptr, b_ptr, A_log_ptr, dt_bias_ptr, q_ptr, k_ptr, v_ptr, g_ptr, beta_ptr, stride_x_tok, stride_a_tok, stride_b_tok, stride_q_tok, stride_k_tok, stride_v_tok, L, H: tl.constexpr, HV: tl.constexpr, K: tl.constexpr, V: tl.constexpr, APPLY_L2NORM: tl.constexpr, L2NORM_EPS: tl.constexpr, OUTPUT_G_EXP: tl.constexpr, SOFTPLUS_THRESHOLD: tl.constexpr, BLOCK_T: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr):\n    \"\"\"Single fused kernel for post-conv1d preparation.\n\n    Grid: (ceil(L, BLOCK_T), H + HV)\n      - program_id(1) in [0, H):    Q/K head processing + l2norm\n      - program_id(1) in [H, H+HV): V head processing + gating\n    \"\"\"\n    i_tb = tl.program_id(0)\n    i_head = tl.program_id(1)\n    HK: tl.constexpr = H * K\n    offs_t = i_tb * BLOCK_T + tl.arange(0, BLOCK_T)\n    mask_t = offs_t < L\n    if i_head < H:\n        i_h = i_head\n        offs_k = tl.arange(0, BK)\n        mask_k = offs_k < K\n        mask_2d = mask_t[:, None] & mask_k[None, :]\n        q_offsets = offs_t[:, None] * stride_x_tok + i_h * K + offs_k[None, :]\n        q_f32 = tl.load(mixed_qkv_ptr + q_offsets, mask=mask_2d, other=0).to(tl.float32)\n        k_offsets = offs_t[:, None] * stride_x_tok + HK + i_h * K + offs_k[None, :]\n        k_f32 = tl.load(mixed_qkv_ptr + k_offsets, mask=mask_2d, other=0).to(tl.float32)\n        if APPLY_L2NORM:\n            q_sq_sum = tl.sum(q_f32 * q_f32, axis=1)\n            q_inv = 1.0 / tl.sqrt(q_sq_sum + L2NORM_EPS)\n            q_f32 = q_f32 * q_inv[:, None]\n            k_sq_sum = tl.sum(k_f32 * k_f32, axis=1)\n            k_inv = 1.0 / tl.sqrt(k_sq_sum + L2NORM_EPS)\n            k_f32 = k_f32 * k_inv[:, None]\n        q_out = offs_t[:, None] * stride_q_tok + i_h * K + offs_k[None, :]\n        tl.store(q_ptr + q_out, q_f32.to(q_ptr.dtype.element_ty), mask=mask_2d)\n        k_out = offs_t[:, None] * stride_k_tok + i_h * K + offs_k[None, :]\n        tl.store(k_ptr + k_out, k_f32.to(k_ptr.dtype.element_ty), mask=mask_2d)\n    else:\n        i_hv = i_head - H\n        offs_v = tl.arange(0, BV)\n        mask_v = offs_v < V\n        mask_2d = mask_t[:, None] & mask_v[None, :]\n        V_OFFSET: tl.constexpr = 2 * H * K\n        v_offsets = offs_t[:, None] * stride_x_tok + V_OFFSET + i_hv * V + offs_v[None, :]\n        v_vals = tl.load(mixed_qkv_ptr + v_offsets, mask=mask_2d, other=0)\n        v_out = offs_t[:, None] * stride_v_tok + i_hv * V + offs_v[None, :]\n        tl.store(v_ptr + v_out, v_vals, mask=mask_2d)\n        A_log_val = tl.load(A_log_ptr + i_hv).to(tl.float32)\n        dt_bias_val = tl.load(dt_bias_ptr + i_hv).to(tl.float32)\n        a_offsets = offs_t * stride_a_tok + i_hv\n        b_offsets = offs_t * stride_b_tok + i_hv\n        a_vals = tl.load(a_ptr + a_offsets, mask=mask_t, other=0).to(tl.float32)\n        b_vals = tl.load(b_ptr + b_offsets, mask=mask_t, other=0).to(tl.float32)\n        x = a_vals + dt_bias_val\n        sp = tl.where(x > 0, x + tl.log(1.0 + tl.exp(-x)), tl.log(1.0 + tl.exp(x)))\n        sp = tl.where(x <= SOFTPLUS_THRESHOLD, sp, x)\n        g_vals = -tl.exp(A_log_val) * sp\n        if OUTPUT_G_EXP:\n            g_vals = tl.exp(g_vals)\n        beta_vals = tl.sigmoid(b_vals)\n        gb_offsets = offs_t * HV + i_hv\n        tl.store(g_ptr + gb_offsets, g_vals, mask=mask_t)\n        tl.store(beta_ptr + gb_offsets, beta_vals, mask=mask_t)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fla/ops/fused_gdn_prefill_post_conv.py"
    },
    {
        "id": "gdn_attention_core",
        "coords": [
            16,
            26,
            21
        ],
        "fiber": 1,
        "logic": "def gdn_attention_core(mixed_qkv: torch.Tensor, b: torch.Tensor, a: torch.Tensor, core_attn_out: torch.Tensor, layer_name: str) -> None:\n    \"\"\"\n    Custom op for the core attention computation.\n    Only handles the convolution + recurrent attention part.\n    Input/output projections are handled outside this op.\n    \"\"\"\n    forward_context: ForwardContext = get_forward_context()\n    self = forward_context.no_compile_layers[layer_name]\n    self._forward_core(mixed_qkv=mixed_qkv, b=b, a=a, core_attn_out=core_attn_out)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/gdn_linear_attn.py"
    },
    {
        "id": "gdn_attention_core_fake",
        "coords": [
            1,
            23,
            30
        ],
        "fiber": 23,
        "logic": "def gdn_attention_core_fake(mixed_qkv: torch.Tensor, b: torch.Tensor, a: torch.Tensor, core_attn_out: torch.Tensor, layer_name: str) -> None:\n    \"\"\"Fake implementation for torch.compile.\"\"\"\n    return",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/gdn_linear_attn.py"
    },
    {
        "id": "fused_gdn_gating_kernel",
        "coords": [
            16,
            25,
            28
        ],
        "fiber": 7,
        "logic": "@triton.jit\ndef fused_gdn_gating_kernel(g, beta_output, A_log, a, b, dt_bias, seq_len, NUM_HEADS: tl.constexpr, beta: tl.constexpr, threshold: tl.constexpr, BLK_HEADS: tl.constexpr):\n    i_b, i_s, i_d = (tl.program_id(0), tl.program_id(1), tl.program_id(2))\n    head_off = i_d * BLK_HEADS + tl.arange(0, BLK_HEADS)\n    off = i_b * seq_len * NUM_HEADS + i_s * NUM_HEADS + head_off\n    mask = head_off < NUM_HEADS\n    blk_A_log = tl.load(A_log + head_off, mask=mask)\n    blk_a = tl.load(a + off, mask=mask)\n    blk_b = tl.load(b + off, mask=mask)\n    blk_bias = tl.load(dt_bias + head_off, mask=mask)\n    x = blk_a.to(tl.float32) + blk_bias.to(tl.float32)\n    softplus_x = tl.where(beta * x <= threshold, 1 / beta * tl.log(1 + tl.exp(beta * x)), x)\n    blk_g = -tl.exp(blk_A_log.to(tl.float32)) * softplus_x\n    tl.store(g + off, blk_g.to(g.dtype.element_ty), mask=mask)\n    blk_beta_output = tl.sigmoid(blk_b.to(tl.float32))\n    tl.store(beta_output + off, blk_beta_output.to(beta_output.dtype.element_ty), mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/gdn_linear_attn.py"
    },
    {
        "id": "_warmup_prefill_kernels",
        "coords": [
            16,
            28,
            0
        ],
        "fiber": 13,
        "logic": "def _warmup_prefill_kernels(self, mixed_qkv: torch.Tensor) -> None:\n    \"\"\"Warm up GDN prefill kernels during V1 profiling.\n\n        During V1 profile runs, ``_forward_core`` returns early because\n        ``attn_metadata`` is ``None``, so the autotuned kernels used by\n        ``chunk_gated_delta_rule`` (e.g. ``solve_tril``,\n        ``chunk_scaled_dot_kkt``) are never invoked.  After profiling,\n        vLLM allocates KV cache using most of the remaining GPU memory.\n        When the first real inference triggers the autotuner it OOMs\n        because there is not enough memory left for benchmarking.\n\n        This method runs minimal forward passes through\n        ``chunk_gated_delta_rule`` with small dummy tensors to force\n        autotuning while GPU memory is still plentiful.  The autotuner\n        results are cached globally, so only the first layer incurs\n        actual benchmarking cost.\n\n        All kernels including ``chunk_fwd_kernel_o`` now use a fixed\n        ``BT = chunk_size`` (64).  A single warmup pass with T = 64\n        is sufficient to populate the autotuner cache.\n\n        The decode path uses ``fused_sigmoid_gating_delta_rule_update``\n        which has fixed kernel parameters (no autotuning), so only the\n        prefill (chunked) path needs warming up.\n        \"\"\"\n    if hasattr(self, '_prefill_kernels_warmed_up'):\n        return\n    self._prefill_kernels_warmed_up = True\n    device = mixed_qkv.device\n    dtype = mixed_qkv.dtype\n    num_k_heads = self.num_k_heads // self.tp_size\n    num_v_heads = self.num_v_heads // self.tp_size\n    _, state_dtype = self.get_state_dtype()\n    T = FLA_CHUNK_SIZE\n    q = torch.randn(1, T, num_k_heads, self.head_k_dim, device=device, dtype=dtype)\n    k = torch.randn(1, T, num_k_heads, self.head_k_dim, device=device, dtype=dtype)\n    v = torch.randn(1, T, num_v_heads, self.head_v_dim, device=device, dtype=dtype)\n    dummy_a = torch.randn(T, num_v_heads, device=device, dtype=dtype)\n    dummy_b = torch.randn(T, num_v_heads, device=device, dtype=dtype)\n    g, beta = fused_gdn_gating(self.A_log, dummy_a, dummy_b, self.dt_bias)\n    state = torch.zeros(1, num_v_heads, self.head_v_dim, self.head_k_dim, device=device, dtype=state_dtype)\n    cu_seqlens = torch.tensor([0, T], device=device, dtype=torch.int32)\n    try:\n        self.chunk_gated_delta_rule(q=q, k=k, v=v, g=g, beta=beta, initial_state=state, output_final_state=True, cu_seqlens=cu_seqlens, use_qk_l2norm_in_kernel=True)\n    except Exception:\n        logger.warning('GDN prefill kernel warmup (T=%d) failed for layer %s. First inference may OOM due to autotuner.', T, self.prefix, exc_info=True)\n    else:\n        logger.debug('GDN prefill kernel warmup (T=%d) completed for layer %s', T, self.prefix)\n    finally:\n        del q, k, v, dummy_a, dummy_b, g, beta, state, cu_seqlens\n    torch.accelerator.empty_cache()",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/gdn_linear_attn.py"
    },
    {
        "id": "clear_linear_attention_cache_for_new_sequences",
        "coords": [
            7,
            9,
            2
        ],
        "fiber": 18,
        "logic": "def clear_linear_attention_cache_for_new_sequences(kv_cache: torch.Tensor, state_indices_tensor: torch.Tensor, attn_metadata: LinearAttentionMetadata) -> None:\n    num_prefills = getattr(attn_metadata, 'num_prefills', 0)\n    if num_prefills <= 0:\n        return\n    num_decode_tokens = getattr(attn_metadata, 'num_decode_tokens', 0)\n    for prefill_idx in range(num_prefills):\n        q_start = attn_metadata.query_start_loc[num_decode_tokens + prefill_idx]\n        q_end = attn_metadata.query_start_loc[num_decode_tokens + prefill_idx + 1]\n        query_len = q_end - q_start\n        context_len = attn_metadata.seq_lens[num_decode_tokens + prefill_idx] - query_len\n        if context_len == 0:\n            block_to_clear = state_indices_tensor[num_decode_tokens + prefill_idx]\n            kv_cache[block_to_clear, ...] = 0",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/linear_attn.py"
    },
    {
        "id": "linear_attention_decode",
        "coords": [
            26,
            12,
            3
        ],
        "fiber": 10,
        "logic": "def linear_attention_decode(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, kv_cache: torch.Tensor, slope_rate: torch.Tensor, state_indices_tensor: torch.Tensor, q_start: int=0, q_end: int | None=None, slot_start: int=0, slot_end: int | None=None, block_size: int=32) -> torch.Tensor:\n    q = q[q_start:q_end].unsqueeze(2).contiguous()\n    k = k[q_start:q_end].unsqueeze(2).contiguous()\n    v = v[q_start:q_end].unsqueeze(2).contiguous()\n    slot_id = state_indices_tensor[slot_start:slot_end]\n    return linear_decode_forward_triton(q, k, v, kv_cache, slope_rate, slot_id, block_size)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/linear_attn.py"
    },
    {
        "id": "linear_attention_prefill_and_mix",
        "coords": [
            14,
            7,
            23
        ],
        "fiber": 13,
        "logic": "def linear_attention_prefill_and_mix(q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, kv_cache: torch.Tensor, state_indices_tensor: torch.Tensor, attn_metadata: LinearAttentionMetadata, slope_rate: torch.Tensor, block_size: int, decode_fn: Callable[..., torch.Tensor], prefix_fn: Callable[..., torch.Tensor], layer_idx: int | None=None) -> torch.Tensor:\n    hidden = []\n    for _prefill_idx in range(getattr(attn_metadata, 'num_prefills', 0)):\n        if _prefill_idx >= len(attn_metadata.query_start_loc):\n            break\n        if _prefill_idx >= len(state_indices_tensor):\n            break\n        offset = attn_metadata.num_decode_tokens\n        _start = attn_metadata.query_start_loc[offset + _prefill_idx]\n        _end = attn_metadata.query_start_loc[offset + _prefill_idx + 1]\n        slot_id = state_indices_tensor[offset + _prefill_idx]\n        qs = q[_start:_end].transpose(0, 1).contiguous()\n        ks = k[_start:_end].transpose(0, 1).contiguous()\n        vs = v[_start:_end].transpose(0, 1).contiguous()\n        slice_layer_cache = kv_cache[slot_id, ...]\n        out_slice = prefix_fn(qs, ks, vs, slice_layer_cache, slope_rate, block_size, layer_idx=layer_idx)\n        hidden.append(out_slice.contiguous())\n    if attn_metadata.num_decode_tokens > 0:\n        hidden_decode = decode_fn(q, k, v, kv_cache, state_indices_tensor, attn_metadata)\n        hidden.insert(0, hidden_decode)\n    if not hidden:\n        return torch.empty((0, q.size(-1)), device=q.device, dtype=q.dtype)\n    hidden = torch.concat(hidden, dim=0).contiguous()\n    return hidden",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/linear_attn.py"
    },
    {
        "id": "linear_attention",
        "coords": [
            22,
            30,
            12
        ],
        "fiber": 2,
        "logic": "def linear_attention(hidden_states: torch.Tensor, output: torch.Tensor, positions: torch.Tensor, layer_name: str) -> None:\n    forward_context: ForwardContext = get_forward_context()\n    self = forward_context.no_compile_layers[layer_name]\n    self._forward(hidden_states=hidden_states, output=output, positions=positions)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/linear_attn.py"
    },
    {
        "id": "linear_attention_fake",
        "coords": [
            3,
            28,
            27
        ],
        "fiber": 27,
        "logic": "def linear_attention_fake(hidden_states: torch.Tensor, output: torch.Tensor, positions: torch.Tensor, layer_name: str) -> None:\n    return",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/linear_attn.py"
    },
    {
        "id": "linear_attention_state_dtype",
        "coords": [
            15,
            12,
            9
        ],
        "fiber": 5,
        "logic": "@classmethod\ndef linear_attention_state_dtype(cls, model_dtype: ModelDType | torch.dtype, mamba_cache_dtype: MambaDType) -> tuple[torch.dtype, ...]:\n    if mamba_cache_dtype == 'float32':\n        raise ValueError('fp32 state for minimax is not yet supported')\n    state_dtype = get_kv_cache_torch_dtype(mamba_cache_dtype, model_dtype)\n    return (state_dtype,)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/mamba_utils.py"
    },
    {
        "id": "linear_attention_state_shape",
        "coords": [
            2,
            11,
            7
        ],
        "fiber": 20,
        "logic": "@classmethod\ndef linear_attention_state_shape(cls, num_heads: int, tp_size: int, head_dim: int) -> tuple[tuple[int, int, int], ...]:\n    state_shape = (num_heads // tp_size, head_dim, head_dim)\n    return (state_shape,)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/mamba_utils.py"
    },
    {
        "id": "linear_attention_state_copy_func",
        "coords": [
            24,
            18,
            24
        ],
        "fiber": 4,
        "logic": "@classmethod\ndef linear_attention_state_copy_func(cls):\n    return (get_temporal_copy_spec,)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/mamba_utils.py"
    },
    {
        "id": "_causal_conv1d_fwd_kernel",
        "coords": [
            19,
            27,
            2
        ],
        "fiber": 17,
        "logic": "@triton.jit()\ndef _causal_conv1d_fwd_kernel(x_ptr, w_ptr, bias_ptr, initial_states_ptr, cache_indices_ptr, has_initial_states_ptr, query_start_loc_ptr, batch_ptr, token_chunk_offset_ptr, block_idx_first_scheduled_token, block_idx_last_scheduled_token, initial_state_idx, num_computed_tokens, o_ptr, dim: tl.constexpr, seqlen: tl.int32, num_cache_lines: tl.constexpr, stride_x_dim: tl.constexpr, stride_x_token: tl.constexpr, stride_w_dim: tl.constexpr, stride_w_width: tl.constexpr, stride_istate_seq: tl.constexpr, stride_istate_dim: tl.constexpr, stride_istate_token: tl.constexpr, stride_cache_indices: tl.constexpr, stride_o_dim: tl.constexpr, stride_o_token: tl.constexpr, stride_block_m: tl.constexpr, pad_slot_id: tl.constexpr, null_block_id: tl.constexpr, HAS_BIAS: tl.constexpr, KERNEL_WIDTH: tl.constexpr, SILU_ACTIVATION: tl.constexpr, IS_APC_ENABLED: tl.constexpr, HAS_NULL_BLOCK: tl.constexpr, NP2_STATELEN: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):\n    conv_states_ptr = initial_states_ptr\n    conv_state_indices_ptr = cache_indices_ptr\n    stride_conv_state_seq = stride_istate_seq\n    stride_conv_state_dim = stride_istate_dim\n    stride_conv_state_tok = stride_istate_token\n    state_len = KERNEL_WIDTH - 1\n    idx_seq = tl.load(batch_ptr + tl.program_id(0)).to(tl.int64)\n    chunk_offset = tl.load(token_chunk_offset_ptr + tl.program_id(0))\n    idx_feats = tl.program_id(1) * BLOCK_N + tl.arange(0, BLOCK_N)\n    if idx_seq == pad_slot_id:\n        return\n    sequence_start_index = tl.load(query_start_loc_ptr + idx_seq)\n    sequence_end_index = tl.load(query_start_loc_ptr + idx_seq + 1)\n    seqlen = sequence_end_index - sequence_start_index\n    B_size: tl.constexpr = stride_block_m * BLOCK_M\n    if IS_APC_ENABLED:\n        current_first_index = tl.load(block_idx_first_scheduled_token + idx_seq)\n        current_last_index = tl.load(block_idx_last_scheduled_token + idx_seq)\n        sequence_completed_index = tl.load(num_computed_tokens + idx_seq)\n        sequence_completed_offset_token = sequence_completed_index % B_size\n        seq_completed_offset = B_size - sequence_completed_offset_token\n        seq_end_offset = (seqlen - seq_completed_offset) % B_size\n        last_full_block_token_index = sequence_end_index - seq_end_offset\n        if seq_end_offset == 0:\n            last_full_block_token_index = last_full_block_token_index - B_size\n        n_block_to_fill = current_last_index - current_first_index\n        conv_state_init_index = tl.load(initial_state_idx + idx_seq)\n    else:\n        n_block_to_fill = 0\n        current_last_index = 0\n        conv_state_init_index = 0\n        current_first_index = 0\n        last_full_block_token_index = 0\n    token_offset = BLOCK_M * chunk_offset\n    segment_len = min(BLOCK_M, seqlen - token_offset)\n    x_base = x_ptr + sequence_start_index * stride_x_token + idx_feats * stride_x_dim\n    conv_states_input_coord = tl.load(conv_state_indices_ptr + idx_seq * stride_cache_indices + conv_state_init_index).to(tl.int64)\n    if HAS_NULL_BLOCK:\n        if conv_states_input_coord == null_block_id:\n            return\n    conv_states_base = conv_states_ptr + conv_states_input_coord * stride_conv_state_seq + idx_feats * stride_conv_state_dim\n    w_base = w_ptr + idx_feats * stride_w_dim\n    if chunk_offset == 0:\n        load_init_state = tl.load(has_initial_states_ptr + idx_seq).to(tl.int1)\n        if load_init_state:\n            prior_tokens = conv_states_base + (state_len - 1) * stride_conv_state_tok\n            mask_w = idx_feats < dim\n            if KERNEL_WIDTH == 2:\n                conv_states_ptrs = prior_tokens\n                col0 = tl.load(conv_states_ptrs, mask_w, 0.0)\n            if KERNEL_WIDTH == 3:\n                conv_states_ptrs = prior_tokens\n                col1 = tl.load(conv_states_ptrs, mask_w, 0.0)\n                conv_states_ptrs = prior_tokens - 1 * stride_conv_state_tok\n                col0 = tl.load(conv_states_ptrs, mask_w, 0.0)\n            if KERNEL_WIDTH == 4:\n                conv_states_ptrs = prior_tokens\n                col2 = tl.load(conv_states_ptrs, mask_w, 0.0)\n                conv_states_ptrs = prior_tokens - 1 * stride_conv_state_tok\n                col1 = tl.load(conv_states_ptrs, mask_w, 0.0)\n                conv_states_ptrs = prior_tokens - 2 * stride_conv_state_tok\n                col0 = tl.load(conv_states_ptrs, mask_w, 0.0)\n            if KERNEL_WIDTH == 5:\n                conv_states_ptrs = prior_tokens\n                col3 = tl.load(conv_states_ptrs, mask_w, 0.0)\n                conv_states_ptrs = prior_tokens - 1 * stride_conv_state_tok\n                col2 = tl.load(conv_states_ptrs, mask_w, 0.0)\n                conv_states_ptrs = prior_tokens - 2 * stride_conv_state_tok\n                col1 = tl.load(conv_states_ptrs, mask_w, 0.0)\n                conv_states_ptrs = prior_tokens - 3 * stride_conv_state_tok\n                col0 = tl.load(conv_states_ptrs, mask_w, 0.0)\n        else:\n            if KERNEL_WIDTH >= 2:\n                col0 = tl.zeros((BLOCK_N,), dtype=x_ptr.dtype.element_ty)\n            if KERNEL_WIDTH >= 3:\n                col1 = tl.zeros((BLOCK_N,), dtype=x_ptr.dtype.element_ty)\n            if KERNEL_WIDTH >= 4:\n                col2 = tl.zeros((BLOCK_N,), dtype=x_ptr.dtype.element_ty)\n            if KERNEL_WIDTH >= 5:\n                col3 = tl.zeros((BLOCK_N,), dtype=x_ptr.dtype.element_ty)\n        if state_len <= seqlen:\n            idx_tokens_last = seqlen - state_len + tl.arange(0, NP2_STATELEN)\n            x_ptrs = x_ptr + ((sequence_start_index + idx_tokens_last) * stride_x_token)[:, None] + (idx_feats * stride_x_dim)[None, :]\n            mask_x = (idx_tokens_last >= 0)[:, None] & (idx_tokens_last < seqlen)[:, None] & (idx_feats < dim)[None, :]\n            loaded_x = tl.load(x_ptrs, mask_x, 0.0)\n            idx_tokens_conv = tl.arange(0, NP2_STATELEN)\n            conv_states_output_coord = tl.load(conv_state_indices_ptr + idx_seq * stride_cache_indices + current_last_index).to(tl.int64)\n            conv_states_ptrs_target = (conv_states_ptr + conv_states_output_coord * stride_conv_state_seq + idx_feats * stride_conv_state_dim)[None, :] + (idx_tokens_conv * stride_conv_state_tok)[:, None]\n            mask = (idx_tokens_conv < state_len)[:, None] & (idx_feats < dim)[None, :]\n            tl.debug_barrier()\n            tl.store(conv_states_ptrs_target, loaded_x, mask)\n        elif load_init_state:\n            idx_tokens_conv = tl.arange(0, NP2_STATELEN)\n            conv_states_ptrs_source = conv_states_ptr + conv_states_input_coord * stride_conv_state_seq + (idx_feats * stride_conv_state_dim)[None, :] + ((idx_tokens_conv + seqlen) * stride_conv_state_tok)[:, None]\n            mask = (conv_states_input_coord < num_cache_lines) & (idx_tokens_conv + seqlen < state_len)[:, None] & (idx_feats < dim)[None, :]\n            conv_state = tl.load(conv_states_ptrs_source, mask, other=0.0)\n            VAL = state_len - seqlen\n            x_ptrs = x_base[None, :] + ((idx_tokens_conv - VAL) * stride_x_token)[:, None]\n            mask_x = (idx_tokens_conv - VAL >= 0)[:, None] & (idx_tokens_conv - VAL < seqlen)[:, None] & (idx_feats < dim)[None, :]\n            loaded_x = tl.load(x_ptrs, mask_x, 0.0)\n            tl.debug_barrier()\n            new_conv_state = tl.where(mask, conv_state, loaded_x)\n            conv_states_ptrs_target = conv_states_base + (idx_tokens_conv * stride_conv_state_tok)[:, None]\n            mask = (idx_tokens_conv < state_len)[:, None] & (idx_feats < dim)[None, :]\n            tl.store(conv_states_ptrs_target, new_conv_state, mask)\n        else:\n            idx_tokens_conv = tl.arange(0, NP2_STATELEN)\n            VAL = state_len - seqlen\n            x_ptrs = x_base[None, :] + ((idx_tokens_conv - VAL) * stride_x_token)[:, None]\n            mask_x = (idx_tokens_conv - VAL >= 0)[:, None] & (idx_tokens_conv - VAL < seqlen)[:, None] & (idx_feats < dim)[None, :]\n            new_conv_state = tl.load(x_ptrs, mask_x, 0.0)\n            conv_states_ptrs_target = conv_states_base + (idx_tokens_conv * stride_conv_state_tok)[:, None]\n            mask = (idx_tokens_conv < state_len)[:, None] & (idx_feats < dim)[None, :]\n            tl.store(conv_states_ptrs_target, new_conv_state, mask)\n    else:\n        load_init_state = True\n        prior_tokens = x_base + (token_offset - 1) * stride_x_token\n        mask_w = idx_feats < dim\n        if KERNEL_WIDTH == 2:\n            conv_states_ptrs = prior_tokens\n            col0 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n        if KERNEL_WIDTH == 3:\n            conv_states_ptrs = prior_tokens\n            col1 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n            conv_states_ptrs = prior_tokens - 1 * stride_x_token\n            col0 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n        if KERNEL_WIDTH == 4:\n            conv_states_ptrs = prior_tokens\n            col2 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n            conv_states_ptrs = prior_tokens - 1 * stride_x_token\n            col1 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n            conv_states_ptrs = prior_tokens - 2 * stride_x_token\n            col0 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n        if KERNEL_WIDTH == 5:\n            conv_states_ptrs = prior_tokens\n            col3 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n            conv_states_ptrs = prior_tokens - 1 * stride_x_token\n            col2 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n            conv_states_ptrs = prior_tokens - 2 * stride_x_token\n            col1 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n            conv_states_ptrs = prior_tokens - 3 * stride_x_token\n            col0 = tl.load(conv_states_ptrs, mask_w, 0.0, cache_modifier='.ca')\n        if chunk_offset - 1 < n_block_to_fill:\n            idx_tokens_last = last_full_block_token_index - (n_block_to_fill - chunk_offset) * B_size - state_len + tl.arange(0, NP2_STATELEN)\n            x_ptrs = x_ptr + (idx_tokens_last * stride_x_token)[:, None] + (idx_feats * stride_x_dim)[None, :]\n            mask_x = (idx_tokens_last >= 0)[:, None] & (idx_feats < dim)[None, :]\n            loaded_x = tl.load(x_ptrs, mask_x, 0.0)\n            idx_tokens_conv = tl.arange(0, NP2_STATELEN)\n            conv_states_output_coord = tl.load(conv_state_indices_ptr + idx_seq * stride_cache_indices + current_first_index + (chunk_offset - 1)).to(tl.int64)\n            conv_states_ptrs_target = (conv_states_ptr + conv_states_output_coord * stride_conv_state_seq + idx_feats * stride_conv_state_dim)[None, :] + (idx_tokens_conv * stride_conv_state_tok)[:, None]\n            mask = (idx_tokens_conv < state_len)[:, None] & (idx_feats < dim)[None, :]\n            tl.debug_barrier()\n            tl.store(conv_states_ptrs_target, loaded_x, mask)\n    if HAS_BIAS:\n        bias = bias_ptr + idx_feats\n        mask_bias = idx_feats < dim\n        acc_preload = tl.load(bias, mask=mask_bias, other=0.0).to(tl.float32)\n    else:\n        acc_preload = tl.zeros((BLOCK_N,), dtype=tl.float32)\n    x_base_1d = x_base + token_offset * stride_x_token\n    mask_w = idx_feats < dim\n    if KERNEL_WIDTH >= 2:\n        w_ptrs = w_base + 0 * stride_w_width\n        w_col0 = tl.load(w_ptrs, mask_w, other=0.0)\n        w_ptrs = w_base + 1 * stride_w_width\n        w_col1 = tl.load(w_ptrs, mask_w, other=0.0)\n    if KERNEL_WIDTH >= 3:\n        w_ptrs = w_base + 2 * stride_w_width\n        w_col2 = tl.load(w_ptrs, mask_w, other=0.0)\n    if KERNEL_WIDTH >= 4:\n        w_ptrs = w_base + 3 * stride_w_width\n        w_col3 = tl.load(w_ptrs, mask_w, other=0.0)\n    mask_x_1d = idx_feats < dim\n    for idx_token in range(segment_len):\n        acc = acc_preload\n        matrix_w = w_col0\n        matrix_x = col0\n        for j in tl.static_range(KERNEL_WIDTH):\n            if KERNEL_WIDTH == 2:\n                if j == 1:\n                    matrix_w = w_col1\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            elif KERNEL_WIDTH == 3:\n                if j == 1:\n                    matrix_w = w_col1\n                    matrix_x = col1\n                elif j == 2:\n                    matrix_w = w_col2\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            elif KERNEL_WIDTH == 4:\n                if j == 1:\n                    matrix_w = w_col1\n                    matrix_x = col1\n                elif j == 2:\n                    matrix_w = w_col2\n                    matrix_x = col2\n                elif j == 3:\n                    matrix_w = w_col3\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            acc += matrix_x * matrix_w\n        if KERNEL_WIDTH == 2:\n            col0 = matrix_x\n        elif KERNEL_WIDTH == 3:\n            col0 = col1\n            col1 = matrix_x\n        elif KERNEL_WIDTH == 4:\n            col0 = col1\n            col1 = col2\n            col2 = matrix_x\n        if SILU_ACTIVATION:\n            acc = acc / (1 + tl.exp(-acc))\n        mask_1d = (idx_token < segment_len) & (idx_feats < dim)\n        o_ptrs = o_ptr + (sequence_start_index + token_offset + idx_token) * stride_o_token + idx_feats * stride_o_dim\n        tl.store(o_ptrs, acc, mask=mask_1d)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/causal_conv1d.py"
    },
    {
        "id": "_causal_conv1d_update_kernel",
        "coords": [
            7,
            12,
            22
        ],
        "fiber": 10,
        "logic": "@triton.jit()\ndef _causal_conv1d_update_kernel(x_ptr, w_ptr, bias_ptr, conv_state_ptr, conv_state_indices_ptr, num_accepted_tokens_ptr, query_start_loc_ptr, block_idx_last_scheduled_token, initial_state_idx, o_ptr, batch: int, dim: tl.constexpr, seqlen: tl.constexpr, state_len: tl.constexpr, num_cache_lines: tl.constexpr, stride_x_seq: tl.constexpr, stride_x_dim: tl.constexpr, stride_x_token: tl.constexpr, stride_w_dim: tl.constexpr, stride_w_width: tl.constexpr, stride_conv_state_seq: tl.constexpr, stride_conv_state_dim: tl.constexpr, stride_conv_state_tok: tl.constexpr, stride_state_indices: tl.constexpr, stride_o_seq: tl.constexpr, stride_o_dim: tl.constexpr, stride_o_token: tl.constexpr, null_block_id: tl.constexpr, HAS_BIAS: tl.constexpr, KERNEL_WIDTH: tl.constexpr, SILU_ACTIVATION: tl.constexpr, IS_VARLEN: tl.constexpr, IS_APC_ENABLED: tl.constexpr, IS_SPEC_DECODING: tl.constexpr, NP2_STATELEN: tl.constexpr, HAS_NULL_BLOCK: tl.constexpr, BLOCK_N: tl.constexpr):\n    idx_seq = tl.program_id(0)\n    if idx_seq >= batch:\n        return\n    idx_feats = tl.program_id(1) * BLOCK_N + tl.arange(0, BLOCK_N)\n    if IS_APC_ENABLED:\n        conv_state_init = tl.load(initial_state_idx + idx_seq)\n        current_last_index = tl.load(block_idx_last_scheduled_token + idx_seq)\n    else:\n        conv_state_init = 0\n        current_last_index = 0\n    conv_states_input_coord = tl.load(conv_state_indices_ptr + idx_seq * stride_state_indices + conv_state_init).to(tl.int64)\n    if HAS_NULL_BLOCK:\n        if conv_states_input_coord == null_block_id:\n            return\n    if IS_VARLEN:\n        query_start_index = tl.load(query_start_loc_ptr + idx_seq).to(tl.int64)\n        query_end_index = tl.load(query_start_loc_ptr + (idx_seq + 1)).to(tl.int64)\n        state_len = state_len - (seqlen - (query_end_index - query_start_index))\n        seqlen = query_end_index - query_start_index\n        x_offset = query_start_index * stride_x_token\n        o_offset = query_start_index * stride_o_token\n    else:\n        query_start_index = idx_seq * seqlen\n        query_end_index = query_start_index + seqlen\n        x_offset = idx_seq * stride_x_seq\n        o_offset = idx_seq * stride_o_seq\n    if query_start_index == query_end_index:\n        return\n    if IS_SPEC_DECODING:\n        conv_state_token_offset = tl.load(num_accepted_tokens_ptr + idx_seq).to(tl.int64) - 1\n    else:\n        conv_state_token_offset = 0\n    conv_states_base = conv_state_ptr + conv_states_input_coord * stride_conv_state_seq + idx_feats * stride_conv_state_dim\n    mask_w = idx_feats < dim\n    prior_tokens = conv_states_base + conv_state_token_offset * stride_conv_state_tok\n    if KERNEL_WIDTH >= 2:\n        conv_states_ptrs = prior_tokens\n        col0 = tl.load(conv_states_ptrs, mask_w, 0.0)\n    if KERNEL_WIDTH >= 3:\n        conv_states_ptrs = prior_tokens + 1 * stride_conv_state_tok\n        col1 = tl.load(conv_states_ptrs, mask_w, 0.0)\n    if KERNEL_WIDTH >= 4:\n        conv_states_ptrs = prior_tokens + 2 * stride_conv_state_tok\n        col2 = tl.load(conv_states_ptrs, mask_w, 0.0)\n    if KERNEL_WIDTH >= 5:\n        conv_states_ptrs = prior_tokens + 3 * stride_conv_state_tok\n        col3 = tl.load(conv_states_ptrs, mask_w, 0.0)\n    if KERNEL_WIDTH >= 6:\n        conv_states_ptrs = prior_tokens + 4 * stride_conv_state_tok\n        col4 = tl.load(conv_states_ptrs, mask_w, 0.0)\n    idx_tokens = tl.arange(0, NP2_STATELEN)\n    conv_state_ptrs_source = conv_state_ptr + conv_states_input_coord * stride_conv_state_seq + conv_state_token_offset * stride_conv_state_tok + (idx_feats * stride_conv_state_dim)[None, :] + ((idx_tokens + (1 if IS_SPEC_DECODING else seqlen)) * stride_conv_state_tok)[:, None]\n    mask = (conv_states_input_coord < num_cache_lines) & (idx_tokens + seqlen < state_len)[:, None] & (idx_feats < dim)[None, :]\n    conv_state = tl.load(conv_state_ptrs_source, mask, other=0.0)\n    VAL = state_len - seqlen\n    x_base = x_ptr + x_offset + idx_feats * stride_x_dim\n    x_ptrs = x_base[None, :] + ((idx_tokens - VAL) * stride_x_token)[:, None]\n    mask_x = (idx_tokens - VAL >= 0)[:, None] & (idx_tokens - VAL < seqlen)[:, None] & (idx_feats < dim)[None, :]\n    loaded_x = tl.load(x_ptrs, mask_x, 0.0)\n    tl.debug_barrier()\n    new_conv_state = tl.where(mask, conv_state, loaded_x)\n    conv_states_offset = tl.load(conv_state_indices_ptr + idx_seq * stride_state_indices + current_last_index).to(tl.int64)\n    conv_state_ptrs_target = (conv_state_ptr + conv_states_offset * stride_conv_state_seq + idx_feats * stride_conv_state_dim)[None, :] + (idx_tokens * stride_conv_state_tok)[:, None]\n    mask = (idx_tokens < state_len)[:, None] & (idx_feats < dim)[None, :]\n    tl.store(conv_state_ptrs_target, new_conv_state, mask)\n    if HAS_BIAS:\n        bias = bias_ptr + idx_feats\n        mask_bias = idx_feats < dim\n        acc_preload = tl.load(bias, mask=mask_bias, other=0.0).to(tl.float32)\n    else:\n        acc_preload = tl.zeros((BLOCK_N,), dtype=tl.float32)\n    w_base = w_ptr + idx_feats * stride_w_dim\n    mask_w = idx_feats < dim\n    if KERNEL_WIDTH >= 2:\n        w_ptrs = w_base + 0 * stride_w_width\n        w_col0 = tl.load(w_ptrs, mask_w, other=0.0)\n        w_ptrs = w_base + 1 * stride_w_width\n        w_col1 = tl.load(w_ptrs, mask_w, other=0.0)\n    if KERNEL_WIDTH >= 3:\n        w_ptrs = w_base + 2 * stride_w_width\n        w_col2 = tl.load(w_ptrs, mask_w, other=0.0)\n    if KERNEL_WIDTH >= 4:\n        w_ptrs = w_base + 3 * stride_w_width\n        w_col3 = tl.load(w_ptrs, mask_w, other=0.0)\n    if KERNEL_WIDTH >= 5:\n        w_ptrs = w_base + 4 * stride_w_width\n        w_col4 = tl.load(w_ptrs, mask_w, other=0.0)\n    if KERNEL_WIDTH >= 6:\n        w_ptrs = w_base + 5 * stride_w_width\n        w_col5 = tl.load(w_ptrs, mask_w, other=0.0)\n    x_base_1d = x_base\n    mask_x_1d = idx_feats < dim\n    for idx_token in tl.range(seqlen):\n        acc = acc_preload\n        matrix_w = w_col0\n        matrix_x = col0\n        for j in tl.static_range(KERNEL_WIDTH):\n            if KERNEL_WIDTH == 2:\n                if j == 1:\n                    matrix_w = w_col1\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            elif KERNEL_WIDTH == 3:\n                if j == 1:\n                    matrix_w = w_col1\n                    matrix_x = col1\n                elif j == 2:\n                    matrix_w = w_col2\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            elif KERNEL_WIDTH == 4:\n                if j == 1:\n                    matrix_w = w_col1\n                    matrix_x = col1\n                elif j == 2:\n                    matrix_w = w_col2\n                    matrix_x = col2\n                elif j == 3:\n                    matrix_w = w_col3\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            elif KERNEL_WIDTH == 5:\n                if j == 1:\n                    matrix_w = w_col1\n                    matrix_x = col1\n                elif j == 2:\n                    matrix_w = w_col2\n                    matrix_x = col2\n                elif j == 3:\n                    matrix_w = w_col3\n                    matrix_x = col3\n                elif j == 4:\n                    matrix_w = w_col4\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            elif KERNEL_WIDTH == 6:\n                if j == 1:\n                    matrix_w = w_col1\n                    matrix_x = col1\n                elif j == 2:\n                    matrix_w = w_col2\n                    matrix_x = col2\n                elif j == 3:\n                    matrix_w = w_col3\n                    matrix_x = col3\n                elif j == 4:\n                    matrix_w = w_col4\n                    matrix_x = col4\n                elif j == 5:\n                    matrix_w = w_col5\n                    x_ptrs_1d = x_base_1d + idx_token * stride_x_token\n                    matrix_x = tl.load(x_ptrs_1d, mask=mask_x_1d)\n            acc += matrix_x * matrix_w\n        if KERNEL_WIDTH == 2:\n            col0 = matrix_x\n        elif KERNEL_WIDTH == 3:\n            col0 = col1\n            col1 = matrix_x\n        elif KERNEL_WIDTH == 4:\n            col0 = col1\n            col1 = col2\n            col2 = matrix_x\n        elif KERNEL_WIDTH == 5:\n            col0 = col1\n            col1 = col2\n            col2 = col3\n            col3 = matrix_x\n        elif KERNEL_WIDTH == 6:\n            col0 = col1\n            col1 = col2\n            col2 = col3\n            col3 = col4\n            col4 = matrix_x\n        if SILU_ACTIVATION:\n            acc = acc / (1 + tl.exp(-acc))\n        mask_1d = (idx_token < seqlen) & (idx_feats < dim)\n        o_ptrs = o_ptr + o_offset + idx_token * stride_o_token + idx_feats * stride_o_dim\n        tl.store(o_ptrs, acc, mask=mask_1d)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/causal_conv1d.py"
    },
    {
        "id": "_chunk_cumsum_fwd_kernel",
        "coords": [
            17,
            9,
            26
        ],
        "fiber": 21,
        "logic": "@triton.autotune(configs=[triton.Config({'BLOCK_SIZE_H': 2}), triton.Config({'BLOCK_SIZE_H': 4}), triton.Config({'BLOCK_SIZE_H': 8}), triton.Config({'BLOCK_SIZE_H': 16}), triton.Config({'BLOCK_SIZE_H': 32}), triton.Config({'BLOCK_SIZE_H': 64})], key=['chunk_size', 'nheads'])\n@triton.jit\ndef _chunk_cumsum_fwd_kernel(dt_ptr, A_ptr, dt_bias_ptr, dt_out_ptr, dA_cumsum_ptr, cu_chunk_seqlens_ptr, seqlen, nheads: tl.constexpr, chunk_size: tl.constexpr, dt_min: tl.constexpr, dt_max: tl.constexpr, stride_dt_seqlen: tl.int64, stride_dt_head: tl.constexpr, stride_A_head: tl.constexpr, stride_dt_bias_head: tl.constexpr, stride_dt_out_head: tl.int64, stride_dt_out_chunk: tl.int64, stride_dt_out_csize: tl.constexpr, stride_dA_cs_head: tl.int64, stride_dA_cs_chunk: tl.int64, stride_dA_cs_csize: tl.constexpr, DT_SOFTPLUS: tl.constexpr, HAS_DT_BIAS: tl.constexpr, BLOCK_SIZE_H: tl.constexpr, BLOCK_SIZE_CHUNK: tl.constexpr):\n    pid_c = tl.program_id(axis=0).to(tl.int64)\n    pid_h = tl.program_id(axis=1)\n    chunk_seqlen_start = tl.load(cu_chunk_seqlens_ptr + pid_c)\n    chunk_seqlen_end = tl.load(cu_chunk_seqlens_ptr + pid_c + 1)\n    dt_ptr += chunk_seqlen_start * stride_dt_seqlen\n    dt_out_ptr += pid_c * stride_dt_out_chunk\n    dA_cumsum_ptr += pid_c * stride_dA_cs_chunk\n    offs_h = pid_h * BLOCK_SIZE_H + tl.arange(0, BLOCK_SIZE_H)\n    offs_c = tl.arange(0, BLOCK_SIZE_CHUNK)\n    dt_ptrs = dt_ptr + (offs_h[:, None] * stride_dt_head + offs_c[None, :] * stride_dt_seqlen)\n    A_ptrs = A_ptr + offs_h * stride_A_head\n    dt_out_ptrs = dt_out_ptr + (offs_h[:, None] * stride_dt_out_head + offs_c[None, :] * stride_dt_out_csize)\n    dA_cs_ptrs = dA_cumsum_ptr + (offs_h[:, None] * stride_dA_cs_head + offs_c[None, :] * stride_dA_cs_csize)\n    chunk_size_limit = chunk_seqlen_end - chunk_seqlen_start\n    dt = tl.load(dt_ptrs, mask=(offs_h[:, None] < nheads) & (offs_c[None, :] < chunk_size_limit), other=0.0).to(tl.float32)\n    if HAS_DT_BIAS:\n        dt_bias = tl.load(dt_bias_ptr + offs_h * stride_dt_bias_head, mask=offs_h < nheads, other=0.0).to(tl.float32)\n        dt += dt_bias[:, None]\n    if DT_SOFTPLUS:\n        dt = tl.where(dt <= 20.0, softplus(dt), dt)\n    dt = tl.clamp(dt, dt_min, dt_max)\n    dt = tl.where((offs_h[:, None] < nheads) & (offs_c[None, :] < chunk_size_limit), dt, 0.0)\n    tl.store(dt_out_ptrs, dt, mask=(offs_h[:, None] < nheads) & (offs_c[None, :] < chunk_size))\n    A = tl.load(A_ptrs, mask=offs_h < nheads, other=0.0).to(tl.float32)\n    dA = dt * A[:, None]\n    dA_cs = tl.cumsum(dA, axis=1)\n    tl.store(dA_cs_ptrs, dA_cs, mask=(offs_h[:, None] < nheads) & (offs_c[None, :] < chunk_size))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/ssd_chunk_state.py"
    },
    {
        "id": "_chunk_state_fwd_kernel",
        "coords": [
            19,
            30,
            29
        ],
        "fiber": 16,
        "logic": "@triton.autotune(configs=[triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=3, num_warps=4), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=3, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=3, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64}, num_stages=2, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 64}, num_stages=2, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 64}, num_stages=3, num_warps=8), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=5, num_warps=2), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=5, num_warps=2), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=2)], key=['hdim', 'dstate', 'chunk_size'])\n@triton.jit\ndef _chunk_state_fwd_kernel(x_ptr, b_ptr, states_ptr, dt_ptr, dA_cumsum_ptr, cu_chunk_seqlens_ptr, hdim: tl.constexpr, dstate: tl.constexpr, chunk_size: tl.constexpr, seqlen, nheads_ngroups_ratio: tl.constexpr, stride_x_seqlen: tl.int64, stride_x_head: tl.int64, stride_x_hdim: tl.constexpr, stride_b_seqlen: tl.int64, stride_b_head: tl.int64, stride_b_dstate: tl.constexpr, stride_states_chunk: tl.int64, stride_states_head: tl.int64, stride_states_hdim: tl.int64, stride_states_dstate: tl.constexpr, stride_dt_head: tl.int64, stride_dt_chunk: tl.int64, stride_dt_csize: tl.constexpr, stride_dA_cs_head: tl.int64, stride_dA_cs_chunk: tl.int64, stride_dA_cs_csize: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr):\n    pid_c = tl.program_id(axis=1).to(tl.int64)\n    pid_h = tl.program_id(axis=2)\n    num_pid_n = tl.cdiv(dstate, BLOCK_SIZE_N)\n    pid_m = tl.program_id(axis=0) // num_pid_n\n    pid_n = tl.program_id(axis=0) % num_pid_n\n    chunk_seqlen_start = tl.load(cu_chunk_seqlens_ptr + pid_c)\n    chunk_seqlen_end = tl.load(cu_chunk_seqlens_ptr + pid_c + 1)\n    b_ptr += chunk_seqlen_start * stride_b_seqlen + pid_h // nheads_ngroups_ratio * stride_b_head\n    x_ptr += chunk_seqlen_start * stride_x_seqlen + pid_h * stride_x_head\n    dt_ptr += pid_c * stride_dt_chunk + pid_h * stride_dt_head\n    dA_cumsum_ptr += pid_c * stride_dA_cs_chunk + pid_h * stride_dA_cs_head\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    offs_k = tl.arange(0, BLOCK_SIZE_K)\n    x_ptrs = x_ptr + (offs_m[:, None] * stride_x_hdim + offs_k[None, :] * stride_x_seqlen)\n    b_ptrs = b_ptr + (offs_n[None, :] * stride_b_dstate + offs_k[:, None] * stride_b_seqlen)\n    dt_ptrs = dt_ptr + offs_k * stride_dt_csize\n    dA_cs_last = tl.load(dA_cumsum_ptr + (chunk_size - 1) * stride_dA_cs_csize).to(tl.float32)\n    dA_cumsum_ptrs = dA_cumsum_ptr + offs_k * stride_dA_cs_csize\n    chunk_size_limit = chunk_seqlen_end - chunk_seqlen_start\n    acc = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n    for k in range(0, chunk_size_limit, BLOCK_SIZE_K):\n        x = tl.load(x_ptrs, mask=(offs_m[:, None] < hdim) & (offs_k[None, :] < chunk_size_limit - k), other=0.0)\n        b = tl.load(b_ptrs, mask=(offs_k[:, None] < chunk_size_limit - k) & (offs_n[None, :] < dstate), other=0.0).to(tl.float32)\n        dA_cs_k = tl.load(dA_cumsum_ptrs, mask=offs_k < chunk_size_limit - k, other=0.0).to(tl.float32)\n        dt_k = tl.load(dt_ptrs, mask=offs_k < chunk_size_limit - k, other=0.0).to(tl.float32)\n        scale = fast_exp(tl.minimum(dA_cs_last - dA_cs_k, 0.0)) * dt_k\n        b *= scale[:, None]\n        b = b.to(x_ptr.dtype.element_ty)\n        acc += tl.dot(x, b)\n        x_ptrs += BLOCK_SIZE_K * stride_x_seqlen\n        b_ptrs += BLOCK_SIZE_K * stride_b_seqlen\n        dt_ptrs += BLOCK_SIZE_K * stride_dt_csize\n        dA_cumsum_ptrs += BLOCK_SIZE_K * stride_dA_cs_csize\n    states = acc.to(states_ptr.dtype.element_ty)\n    states_ptr += pid_c * stride_states_chunk + pid_h * stride_states_head\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    states_ptrs = states_ptr + (offs_m[:, None] * stride_states_hdim + offs_n[None, :] * stride_states_dstate)\n    c_mask = (offs_m[:, None] < hdim) & (offs_n[None, :] < dstate)\n    tl.store(states_ptrs, states, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/ssd_chunk_state.py"
    },
    {
        "id": "_chunk_scan_fwd_kernel",
        "coords": [
            25,
            14,
            5
        ],
        "fiber": 13,
        "logic": "@triton.autotune(configs=[triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=2, num_warps=8), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=2, num_warps=8), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=2, num_warps=8), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=3, num_warps=4), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 64}, num_stages=2, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64}, num_stages=1, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=1, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=1, num_warps=4), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=1, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64}, num_stages=2, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=2, num_warps=4), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=2, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 64}, num_stages=3, num_warps=8), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 64}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=5, num_warps=2), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=5, num_warps=2), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=2)], key=['chunk_size', 'hdim', 'dstate', 'IS_CAUSAL'])\n@triton.jit\ndef _chunk_scan_fwd_kernel(cb_ptr, x_ptr, z_ptr, out_ptr, dt_ptr, dA_cumsum_ptr, seq_idx_ptr, C_ptr, states_ptr, D_ptr, initstates_ptr, cu_chunk_seqlens_ptr, chunk_size: tl.constexpr, hdim: tl.constexpr, dstate: tl.constexpr, seqlen, nheads_ngroups_ratio: tl.constexpr, stride_cb_chunk: tl.int64, stride_cb_head: tl.int64, stride_cb_csize_m: tl.int64, stride_cb_csize_k: tl.constexpr, stride_x_seqlen: tl.int64, stride_x_head: tl.int64, stride_x_hdim: tl.constexpr, stride_z_seqlen: tl.int64, stride_z_head: tl.int64, stride_z_hdim: tl.constexpr, stride_out_seqlen: tl.int64, stride_out_head: tl.int64, stride_out_hdim: tl.constexpr, stride_dt_chunk: tl.int64, stride_dt_head: tl.int64, stride_dt_csize: tl.constexpr, stride_dA_cs_chunk: tl.int64, stride_dA_cs_head: tl.int64, stride_dA_cs_csize: tl.constexpr, stride_seq_idx_chunk: tl.constexpr, stride_C_seqlen: tl.int64, stride_C_head: tl.int64, stride_C_dstate: tl.constexpr, stride_states_chunk: tl.int64, stride_states_head: tl.int64, stride_states_hdim: tl.int64, stride_states_dstate: tl.constexpr, stride_init_states_batch: tl.int64, stride_init_states_head: tl.int64, stride_init_states_hdim: tl.int64, stride_init_states_dstate: tl.constexpr, stride_D_head: tl.constexpr, IS_CAUSAL: tl.constexpr, HAS_D: tl.constexpr, D_HAS_HDIM: tl.constexpr, HAS_Z: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, BLOCK_SIZE_DSTATE: tl.constexpr, IS_TRITON_22: tl.constexpr, HAS_INITSTATES: tl.constexpr):\n    pid_c = tl.program_id(axis=1).to(tl.int64)\n    pid_h = tl.program_id(axis=2)\n    num_pid_n = tl.cdiv(hdim, BLOCK_SIZE_N)\n    pid_m = tl.program_id(axis=0) // num_pid_n\n    pid_n = tl.program_id(axis=0) % num_pid_n\n    cb_ptr += pid_c * stride_cb_chunk + pid_h // nheads_ngroups_ratio * stride_cb_head\n    chunk_seqlen_start = tl.load(cu_chunk_seqlens_ptr + pid_c)\n    chunk_seqlen_end = tl.load(cu_chunk_seqlens_ptr + pid_c + 1)\n    x_ptr += chunk_seqlen_start * stride_x_seqlen + pid_h * stride_x_head\n    dt_ptr += pid_c * stride_dt_chunk + pid_h * stride_dt_head\n    dA_cumsum_ptr += pid_c * stride_dA_cs_chunk + pid_h * stride_dA_cs_head\n    C_ptr += chunk_seqlen_start * stride_C_seqlen + pid_h // nheads_ngroups_ratio * stride_C_head\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    seq_idx_ptr += pid_c * stride_seq_idx_chunk\n    seq_idx = tl.load(seq_idx_ptr)\n    seq_idx_prev = tl.load(seq_idx_ptr - stride_seq_idx_chunk, mask=pid_c >= 1, other=-1)\n    if HAS_INITSTATES and seq_idx != seq_idx_prev:\n        prev_states_ptr = initstates_ptr + seq_idx * stride_init_states_batch + pid_h * stride_init_states_head\n        prev_states_hdim = stride_init_states_hdim\n        prev_states_dstate = stride_init_states_dstate\n    else:\n        prev_states_ptr = states_ptr + (pid_c - 1) * stride_states_chunk + pid_h * stride_states_head\n        prev_states_hdim = stride_states_hdim\n        prev_states_dstate = stride_states_dstate\n    chunk_size_limit = chunk_seqlen_end - chunk_seqlen_start\n    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    dA_cs_m = tl.load(dA_cumsum_ptr + offs_m * stride_dA_cs_csize, mask=offs_m < chunk_size, other=0.0).to(tl.float32)\n    acc = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n    offs_out_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_out_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    offs_k_dstate = tl.arange(0, BLOCK_SIZE_DSTATE if BLOCK_SIZE_DSTATE <= 128 else BLOCK_SIZE_K)\n    C_ptrs = C_ptr + (offs_m[:, None] * stride_C_seqlen + offs_k_dstate[None, :] * stride_C_dstate)\n    scale_m = fast_exp(dA_cs_m)\n    if BLOCK_SIZE_DSTATE <= 128:\n        C = tl.load(C_ptrs, mask=(offs_m[:, None] < chunk_size_limit) & (offs_k_dstate[None, :] < dstate), other=0.0)\n        if not HAS_INITSTATES and seq_idx != seq_idx_prev:\n            prev_states = tl.zeros((BLOCK_SIZE_DSTATE, BLOCK_SIZE_N), dtype=C_ptr.dtype.element_ty)\n        else:\n            prev_states_ptrs = prev_states_ptr + offs_n[None, :] * prev_states_hdim + offs_k_dstate[:, None] * prev_states_dstate\n            prev_states = tl.load(prev_states_ptrs, mask=(offs_k_dstate[:, None] < dstate) & (offs_n[None, :] < hdim), other=0.0)\n            prev_states = prev_states.to(C_ptr.dtype.element_ty)\n        acc = tl.dot(C, prev_states) * scale_m[:, None]\n    else:\n        prev_states_ptrs = prev_states_ptr + offs_n[None, :] * prev_states_hdim + offs_k_dstate[:, None] * prev_states_dstate\n        for k in range(0, dstate, BLOCK_SIZE_K):\n            C = tl.load(C_ptrs, mask=(offs_m[:, None] < chunk_size_limit) & (offs_k_dstate[None, :] < dstate - k), other=0.0)\n            if not HAS_INITSTATES and seq_idx != seq_idx_prev:\n                prev_states = tl.zeros((BLOCK_SIZE_K, BLOCK_SIZE_N), dtype=C_ptr.dtype.element_ty)\n            else:\n                prev_states = tl.load(prev_states_ptrs, mask=(offs_k_dstate[:, None] < dstate - k) & (offs_n[None, :] < hdim), other=0.0)\n                prev_states = prev_states.to(C_ptr.dtype.element_ty)\n            acc += tl.dot(C, prev_states)\n            C_ptrs += BLOCK_SIZE_K\n            prev_states_ptrs += BLOCK_SIZE_K\n        acc *= scale_m[:, None]\n    offs_k = tl.arange(0, BLOCK_SIZE_K)\n    cb_ptrs = cb_ptr + (offs_m[:, None] * stride_cb_csize_m + offs_k[None, :] * stride_cb_csize_k)\n    x_ptrs = x_ptr + (offs_k[:, None] * stride_x_seqlen + offs_n[None, :] * stride_x_hdim)\n    dt_ptrs = dt_ptr + offs_k * stride_dt_csize\n    dA_cumsum_ptrs = dA_cumsum_ptr + offs_k * stride_dA_cs_csize\n    K_MAX = chunk_size_limit if not IS_CAUSAL else min((pid_m + 1) * BLOCK_SIZE_M, chunk_size_limit)\n    for k in range(0, K_MAX, BLOCK_SIZE_K):\n        cb = tl.load(cb_ptrs, mask=(offs_m[:, None] < chunk_size) & (offs_k[None, :] < chunk_size - k), other=0.0).to(tl.float32)\n        dA_cs_k = tl.load(dA_cumsum_ptrs, mask=offs_k < chunk_size - k, other=0.0).to(tl.float32)\n        cb *= fast_exp(tl.minimum(dA_cs_m[:, None] - dA_cs_k[None, :], 0.0))\n        dt_k = tl.load(dt_ptrs, mask=offs_k < chunk_size - k, other=0.0).to(tl.float32)\n        cb *= dt_k\n        if IS_CAUSAL:\n            mask = offs_m[:, None] >= k + offs_k[None, :]\n            cb = tl.where(mask, cb, 0.0)\n        cb = cb.to(x_ptr.dtype.element_ty)\n        x = tl.load(x_ptrs, mask=(offs_k[:, None] < chunk_size_limit - k) & (offs_n[None, :] < hdim), other=0.0)\n        acc += tl.dot(cb, x)\n        cb_ptrs += BLOCK_SIZE_K * stride_cb_csize_k\n        x_ptrs += BLOCK_SIZE_K * stride_x_seqlen\n        dt_ptrs += BLOCK_SIZE_K * stride_dt_csize\n        dA_cumsum_ptrs += BLOCK_SIZE_K * stride_dA_cs_csize\n    offs_out_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_out_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    if HAS_D:\n        if D_HAS_HDIM:\n            D = tl.load(D_ptr + pid_h * stride_D_head + offs_n, mask=offs_n < hdim, other=0.0).to(tl.float32)\n        else:\n            D = tl.load(D_ptr + pid_h * stride_D_head).to(tl.float32)\n        x_residual = tl.load(x_ptr + (offs_m[:, None] * stride_x_seqlen + offs_n[None, :] * stride_x_hdim), mask=(offs_m[:, None] < chunk_size_limit) & (offs_n[None, :] < hdim), other=0.0).to(tl.float32)\n        acc += x_residual * D\n    if HAS_Z:\n        z_ptr += chunk_seqlen_start * stride_z_seqlen + pid_h * stride_z_head\n        z_ptrs = z_ptr + (stride_z_seqlen * offs_out_m[:, None] + stride_z_hdim * offs_out_n[None, :])\n        z = tl.load(z_ptrs, mask=(offs_out_m[:, None] < chunk_size_limit) & (offs_out_n[None, :] < hdim), other=0.0).to(tl.float32)\n        acc *= z * tl.sigmoid(z)\n    out_ptr += chunk_seqlen_start * stride_out_seqlen + pid_h * stride_out_head\n    out_ptrs = out_ptr + (stride_out_seqlen * offs_out_m[:, None] + offs_out_n[None, :] * stride_out_hdim)\n    tl.store(out_ptrs, acc, mask=(offs_out_m[:, None] < chunk_size_limit) & (offs_out_n[None, :] < hdim))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/ssd_chunk_scan.py"
    },
    {
        "id": "_bmm_chunk_fwd_kernel",
        "coords": [
            4,
            21,
            11
        ],
        "fiber": 5,
        "logic": "@triton.autotune(configs=[triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 64}, num_stages=3, num_warps=8), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=4), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32}, num_stages=5, num_warps=2), triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=5, num_warps=2), triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}, num_stages=4, num_warps=2)], key=['chunk_size', 'K', 'IS_CAUSAL'])\n@triton.jit\ndef _bmm_chunk_fwd_kernel(a_ptr, b_ptr, out_ptr, cu_chunk_seqlens_ptr, seqlen, chunk_size: tl.constexpr, K: tl.constexpr, ngroups: tl.constexpr, stride_a_seqlen: tl.int64, stride_a_head: tl.int64, stride_ak: tl.constexpr, stride_b_seqlen: tl.int64, stride_b_head: tl.int64, stride_bk: tl.constexpr, stride_out_chunk: tl.int64, stride_out_head: tl.int64, stride_outm: tl.int64, stride_outn: tl.constexpr, IS_CAUSAL: tl.constexpr, dot_dtype: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr):\n    pid_ch = tl.program_id(axis=1).to(tl.int64)\n    pid_c = pid_ch // ngroups\n    pid_h = pid_ch - pid_c * ngroups\n    num_pid_n = tl.cdiv(chunk_size, BLOCK_SIZE_N)\n    pid_m = tl.program_id(axis=0) // num_pid_n\n    pid_n = tl.program_id(axis=0) % num_pid_n\n    if IS_CAUSAL:\n        if pid_n * BLOCK_SIZE_N >= (pid_m + 1) * BLOCK_SIZE_M:\n            return\n    chunk_seqlen_start = tl.load(cu_chunk_seqlens_ptr + pid_c)\n    chunk_seqlen_end = tl.load(cu_chunk_seqlens_ptr + pid_c + 1)\n    a_ptr += chunk_seqlen_start * stride_a_seqlen + pid_h * stride_a_head\n    b_ptr += chunk_seqlen_start * stride_b_seqlen + pid_h * stride_b_head\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    offs_k = tl.arange(0, BLOCK_SIZE_K)\n    a_ptrs = a_ptr + (offs_m[:, None] * stride_a_seqlen + offs_k[None, :] * stride_ak)\n    b_ptrs = b_ptr + (offs_k[:, None] * stride_bk + offs_n[None, :] * stride_b_seqlen)\n    chunk_size_limit = chunk_seqlen_end - chunk_seqlen_start\n    acc = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K)):\n        a = tl.load(a_ptrs, mask=(offs_m[:, None] < chunk_size_limit) & (offs_k[None, :] < K - k * BLOCK_SIZE_K), other=0.0).to(dot_dtype)\n        b = tl.load(b_ptrs, mask=(offs_k[:, None] < K - k * BLOCK_SIZE_K) & (offs_n[None, :] < chunk_size_limit), other=0.0).to(dot_dtype)\n        acc += tl.dot(a, b)\n        a_ptrs += BLOCK_SIZE_K * stride_ak\n        b_ptrs += BLOCK_SIZE_K * stride_bk\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    out = acc.to(out_ptr.dtype.element_ty)\n    out_ptr += pid_c * stride_out_chunk + pid_h * stride_out_head\n    out_ptrs = out_ptr + (stride_outm * offs_m[:, None] + offs_n[None, :] * stride_outn)\n    tl.store(out_ptrs, out, mask=(offs_m[:, None] < chunk_size) & (offs_n[None, :] < chunk_size))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/ssd_bmm.py"
    },
    {
        "id": "_layer_norm_fwd_1pass_kernel",
        "coords": [
            18,
            20,
            8
        ],
        "fiber": 15,
        "logic": "@triton.heuristics({'HAS_BIAS': lambda args: args['B'] is not None})\n@triton.heuristics({'HAS_Z': lambda args: args['Z'] is not None})\n@triton.jit\ndef _layer_norm_fwd_1pass_kernel(X, Y, W, B, Z, Mean, Rstd, stride_x_row: tl.int64, stride_y_row: tl.int64, stride_z_row: tl.int64, M: tl.int64, N: tl.int64, eps, BLOCK_N: tl.constexpr, HAS_BIAS: tl.constexpr, HAS_Z: tl.constexpr, NORM_BEFORE_GATE: tl.constexpr, IS_RMS_NORM: tl.constexpr):\n    row = tl.program_id(0)\n    group = tl.program_id(1)\n    X += row * stride_x_row + group * N\n    Y += row * stride_y_row + group * N\n    if HAS_Z:\n        Z += row * stride_z_row + group * N\n    if not IS_RMS_NORM:\n        Mean += group * M\n    Rstd += group * M\n    W += group * N\n    if HAS_BIAS:\n        B += group * N\n    cols = tl.arange(0, BLOCK_N)\n    x = tl.load(X + cols, mask=cols < N, other=0.0).to(tl.float32)\n    if HAS_Z and (not NORM_BEFORE_GATE):\n        z = tl.load(Z + cols, mask=cols < N).to(tl.float32)\n        x *= z * tl.sigmoid(z)\n    if not IS_RMS_NORM:\n        mean = tl.sum(x, axis=0) / N\n        tl.store(Mean + row, mean)\n        xbar = tl.where(cols < N, x - mean, 0.0)\n        var = tl.sum(xbar * xbar, axis=0) / N\n    else:\n        xbar = tl.where(cols < N, x, 0.0)\n        var = tl.sum(xbar * xbar, axis=0) / N\n    rstd = 1 / tl.sqrt(var + eps)\n    tl.store(Rstd + row, rstd)\n    mask = cols < N\n    w = tl.load(W + cols, mask=mask).to(tl.float32)\n    if HAS_BIAS:\n        b = tl.load(B + cols, mask=mask).to(tl.float32)\n    x_hat = (x - mean) * rstd if not IS_RMS_NORM else x * rstd\n    y = x_hat * w + b if HAS_BIAS else x_hat * w\n    if HAS_Z and NORM_BEFORE_GATE:\n        z = tl.load(Z + cols, mask=mask).to(tl.float32)\n        y *= z * tl.sigmoid(z)\n    tl.store(Y + cols, y, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/layernorm_gated.py"
    },
    {
        "id": "_state_passing_fwd_kernel",
        "coords": [
            29,
            17,
            21
        ],
        "fiber": 5,
        "logic": "@triton.autotune(configs=[triton.Config({'BLOCK_SIZE': 64}), triton.Config({'BLOCK_SIZE': 128}), triton.Config({'BLOCK_SIZE': 256}), triton.Config({'BLOCK_SIZE': 512}), triton.Config({'BLOCK_SIZE': 1024}), triton.Config({'BLOCK_SIZE': 2048})], key=['dim'])\n@triton.jit\ndef _state_passing_fwd_kernel(states_ptr, out_ptr, dA_cs_ptr, initstates_ptr, last_chunk_indices_ptr, dim: tl.constexpr, chunk_size: tl.constexpr, stride_states_chunk: tl.int64, stride_states_head: tl.int64, stride_states_dim: tl.constexpr, stride_out_chunk: tl.int64, stride_out_head: tl.int64, stride_out_dim: tl.constexpr, stride_dA_cs_head: tl.int64, stride_dA_cs_chunk: tl.int64, stride_dA_cs_csize: tl.constexpr, stride_initstates_batch: tl.int64, stride_initstates_head: tl.int64, stride_initstates_dim: tl.constexpr, HAS_INITSTATES: tl.constexpr, BLOCK_SIZE: tl.constexpr):\n    pid_m = tl.program_id(axis=0)\n    pid_b = tl.program_id(axis=1)\n    pid_h = tl.program_id(axis=2)\n    chunk_end = tl.load(last_chunk_indices_ptr + pid_b) + 1\n    chunk_start = tl.load(last_chunk_indices_ptr + pid_b - 1, mask=pid_b > 0, other=-1) + 1\n    states_ptr += chunk_start * stride_states_chunk + pid_h * stride_states_head\n    dA_cs_ptr += pid_h * stride_dA_cs_head + chunk_start * stride_dA_cs_chunk + (chunk_size - 1) * stride_dA_cs_csize\n    out_ptr += chunk_start * stride_out_chunk + pid_h * stride_out_head\n    offs_m = pid_m * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)\n    states_ptrs = states_ptr + offs_m * stride_states_dim\n    out_ptrs = out_ptr + offs_m * stride_out_dim\n    if HAS_INITSTATES:\n        initstates_ptrs = initstates_ptr + pid_b * stride_initstates_batch + pid_h * stride_initstates_head + offs_m * stride_initstates_dim\n        states = tl.load(initstates_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n    else:\n        states = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)\n    nchunks_this_seq = chunk_end - chunk_start\n    for _ in range(nchunks_this_seq):\n        new_states = tl.load(states_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n        dA_cs = tl.load(dA_cs_ptr).to(tl.float32)\n        states = fast_exp(dA_cs) * states + new_states\n        tl.store(out_ptrs, states, mask=offs_m < dim)\n        states_ptrs += stride_states_chunk\n        dA_cs_ptr += stride_dA_cs_chunk\n        out_ptrs += stride_out_chunk",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/ssd_state_passing.py"
    },
    {
        "id": "_selective_scan_update_kernel",
        "coords": [
            16,
            13,
            13
        ],
        "fiber": 11,
        "logic": "@triton.heuristics({'HAS_DT_BIAS': lambda args: args['dt_bias_ptr'] is not None})\n@triton.heuristics({'HAS_D': lambda args: args['D_ptr'] is not None})\n@triton.heuristics({'HAS_Z': lambda args: args['z_ptr'] is not None})\n@triton.heuristics({'HAS_STATE_BATCH_INDICES': lambda args: args['state_batch_indices_ptr'] is not None})\n@triton.heuristics({'IS_SPEC_DECODING': lambda args: args['num_accepted_tokens_ptr'] is not None})\n@triton.heuristics({'IS_VARLEN': lambda args: args['cu_seqlens_ptr'] is not None})\n@triton.heuristics({'BLOCK_SIZE_DSTATE': lambda args: triton.next_power_of_2(args['dstate'])})\n@triton.jit(do_not_specialize=['N'])\ndef _selective_scan_update_kernel(state_ptr, rand_seed_ptr, x_ptr, dt_ptr, dt_bias_ptr, A_ptr, B_ptr, C_ptr, D_ptr, z_ptr, out_ptr, state_batch_indices_ptr, dst_state_batch_indices_ptr, null_block_id, num_accepted_tokens_ptr, cu_seqlens_ptr, N, nheads, dim, dstate, nheads_ngroups_ratio, stride_state_batch, stride_state_head, stride_state_dim, stride_state_dstate, stride_x_batch, stride_x_head, stride_x_dim, stride_dt_batch, stride_dt_head, stride_dt_dim, stride_dt_bias_head, stride_dt_bias_dim, stride_A_head, stride_A_dim, stride_A_dstate, stride_B_batch, stride_B_group, stride_B_dstate, stride_C_batch, stride_C_group, stride_C_dstate, stride_D_head, stride_D_dim, stride_z_batch, stride_z_head, stride_z_dim, stride_out_batch, stride_out_head, stride_out_dim, stride_state_indices_batch, stride_state_indices_T, stride_dst_state_indices_batch, stride_dst_state_indices_T, DT_SOFTPLUS: tl.constexpr, TIE_HDIM: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, HAS_DT_BIAS: tl.constexpr, HAS_D: tl.constexpr, HAS_Z: tl.constexpr, HAS_STATE_BATCH_INDICES: tl.constexpr, IS_SPEC_DECODING: tl.constexpr, IS_VARLEN: tl.constexpr, BLOCK_SIZE_DSTATE: tl.constexpr, USE_RS_ROUNDING: tl.constexpr, PHILOX_ROUNDS: tl.constexpr):\n    pid_m = tl.program_id(axis=0)\n    pid_b = tl.program_id(axis=1)\n    pid_h = tl.program_id(axis=2)\n    if IS_VARLEN:\n        bos = tl.load(cu_seqlens_ptr + pid_b).to(tl.int64)\n        eos = tl.load(cu_seqlens_ptr + pid_b + 1).to(tl.int64)\n        seq_len = eos - bos\n        if seq_len == 0:\n            return\n    else:\n        bos = pid_b\n        seq_len = 1\n    state_ptr_base = state_ptr\n    if HAS_STATE_BATCH_INDICES:\n        if IS_SPEC_DECODING:\n            num_accepted = tl.load(num_accepted_tokens_ptr + pid_b).to(tl.int64)\n            init_token_idx = tl.maximum(num_accepted - 1, 0)\n        else:\n            init_token_idx = 0\n        dst_state_batch_indices_ptr += pid_b * stride_dst_state_indices_batch\n        if not IS_SPEC_DECODING:\n            dst_state_batch_idx = tl.load(dst_state_batch_indices_ptr + init_token_idx * stride_dst_state_indices_T).to(tl.int64)\n            dst_state_ptr = state_ptr + (dst_state_batch_idx * stride_state_batch + pid_h * stride_state_head)\n        state_batch_indices_ptr += pid_b * stride_state_indices_batch + init_token_idx * stride_state_indices_T\n        state_batch_idx = tl.load(state_batch_indices_ptr).to(tl.int64)\n        state_ptr += state_batch_idx * stride_state_batch + pid_h * stride_state_head\n    else:\n        dst_state_ptr = state_ptr + pid_b * stride_state_batch + pid_h * stride_state_head\n        state_ptr += pid_b * stride_state_batch + pid_h * stride_state_head\n    x_ptr += bos * stride_x_batch + pid_h * stride_x_head\n    dt_ptr += bos * stride_dt_batch + pid_h * stride_dt_head\n    if HAS_DT_BIAS:\n        dt_bias_ptr += pid_h * stride_dt_bias_head\n    A_ptr += pid_h * stride_A_head\n    B_ptr += bos * stride_B_batch + pid_h // nheads_ngroups_ratio * stride_B_group\n    C_ptr += bos * stride_C_batch + pid_h // nheads_ngroups_ratio * stride_C_group\n    if HAS_Z:\n        z_ptr += bos * stride_z_batch + pid_h * stride_z_head\n    out_ptr += bos * stride_out_batch + pid_h * stride_out_head\n    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)\n    offs_n = tl.arange(0, BLOCK_SIZE_DSTATE)\n    state_ptrs = state_ptr + (offs_m[:, None] * stride_state_dim + offs_n[None, :] * stride_state_dstate)\n    if not IS_SPEC_DECODING:\n        dst_state_ptrs = dst_state_ptr + (offs_m[:, None] * stride_state_dim + offs_n[None, :] * stride_state_dstate)\n    mask = (offs_m[:, None] < dim) & (offs_n[None, :] < dstate)\n    if HAS_STATE_BATCH_INDICES:\n        mask &= state_batch_idx != null_block_id\n    state = tl.load(state_ptrs, mask=mask, other=0.0).to(tl.float32)\n    if HAS_DT_BIAS:\n        dt_bias_ptrs = dt_bias_ptr + offs_m * stride_dt_bias_dim\n    if HAS_D:\n        D_ptr += pid_h * stride_D_head\n        D_ptrs = D_ptr + offs_m * stride_D_dim\n    A_ptrs = A_ptr + offs_m[:, None] * stride_A_dim + offs_n[None, :] * stride_A_dstate\n    for i_t in range(seq_len):\n        x_ptrs = x_ptr + offs_m * stride_x_dim\n        dt_ptrs = dt_ptr + offs_m * stride_dt_dim\n        B_ptrs = B_ptr + offs_n * stride_B_dstate\n        C_ptrs = C_ptr + offs_n * stride_C_dstate\n        if HAS_Z:\n            z_ptrs = z_ptr + offs_m * stride_z_dim\n        out_ptrs = out_ptr + offs_m * stride_out_dim\n        x = tl.load(x_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n        if not TIE_HDIM:\n            dt = tl.load(dt_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n            if HAS_DT_BIAS:\n                dt += tl.load(dt_bias_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n            if DT_SOFTPLUS:\n                dt = softplus(dt)\n            A = tl.load(A_ptrs, mask=(offs_m[:, None] < dim) & (offs_n[None, :] < dstate), other=0.0).to(tl.float32)\n            dA = fast_exp(A * dt[:, None])\n        else:\n            dt = tl.load(dt_ptr).to(tl.float32)\n            if HAS_DT_BIAS:\n                dt += tl.load(dt_bias_ptr).to(tl.float32)\n            if DT_SOFTPLUS:\n                dt = softplus(dt)\n            A = tl.load(A_ptr).to(tl.float32)\n            dA = fast_exp(A * dt)\n        B = tl.load(B_ptrs, mask=offs_n < dstate, other=0.0).to(tl.float32)\n        C = tl.load(C_ptrs, mask=offs_n < dstate, other=0.0).to(tl.float32)\n        if HAS_D:\n            D = tl.load(D_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n        if HAS_Z:\n            z = tl.load(z_ptrs, mask=offs_m < dim, other=0.0).to(tl.float32)\n        dB = B[None, :] * dt[:, None] if not TIE_HDIM else B * dt\n        state = state * dA + dB * x[:, None]\n        if IS_SPEC_DECODING:\n            dst_idx_ptr = dst_state_batch_indices_ptr + i_t * stride_dst_state_indices_T\n            token_dst_idx = tl.load(dst_idx_ptr).to(tl.int64)\n            if token_dst_idx != null_block_id:\n                token_dst_ptrs = state_ptr_base + token_dst_idx * stride_state_batch + pid_h * stride_state_head + offs_m[:, None] * stride_state_dim + offs_n[None, :] * stride_state_dstate\n                tl.store(token_dst_ptrs, state.to(token_dst_ptrs.dtype.element_ty), mask=mask)\n        out = tl.sum(state * C[None, :], axis=1)\n        if HAS_D:\n            out += x * D\n        if HAS_Z:\n            out *= z * tl.sigmoid(z)\n        tl.store(out_ptrs, out, mask=offs_m < dim)\n        x_ptr += stride_x_batch\n        dt_ptr += stride_dt_batch\n        B_ptr += stride_B_batch\n        C_ptr += stride_C_batch\n        out_ptr += stride_out_batch\n        if HAS_Z:\n            z_ptr += stride_z_batch\n    if not IS_SPEC_DECODING:\n        if USE_RS_ROUNDING:\n            rand_seed = tl.load(rand_seed_ptr)\n            if HAS_STATE_BATCH_INDICES:\n                rand_offsets = state_batch_idx * stride_state_batch + pid_h * stride_state_head\n            else:\n                rand_offsets = pid_b * stride_state_batch + pid_h * stride_state_head\n            rand_offsets += offs_m[:, None] * stride_state_dim + offs_n[None, :] * stride_state_dstate\n            if PHILOX_ROUNDS > 0:\n                rand = tl.randint(rand_seed, rand_offsets, PHILOX_ROUNDS)\n            else:\n                rand = tl.randint(rand_seed, rand_offsets)\n            state = convert_rs_fp16x2(state, rand)\n            tl.static_assert(state.dtype == tl.float16, 'state must be fp16')\n            tl.static_assert(dst_state_ptrs.dtype.element_ty == tl.float16, 'dst_state_ptrs must be fp16')\n        else:\n            state = state.to(dst_state_ptrs.dtype.element_ty)\n        tl.store(dst_state_ptrs, state, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/mamba/ops/mamba_ssm.py"
    },
    {
        "id": "triton_kernel_moe_forward",
        "coords": [
            19,
            19,
            11
        ],
        "fiber": 18,
        "logic": "def triton_kernel_moe_forward(hidden_states: torch.Tensor, w1, w2, gating_output: torch.Tensor, topk: int, renormalize: bool, activation: MoEActivation=MoEActivation.SWIGLUOAI, quant_config: FusedMoEQuantConfig | None=None, apply_router_weight_on_input: bool=False, global_num_experts: int=-1, expert_map: torch.Tensor | None=None, unpadded_N_w1=None, unpadded_K_w1=None, unpadded_N_w2=None, unpadded_K_w2=None) -> torch.Tensor:\n    if quant_config is not None and quant_config.use_mxfp4_w4a8 and rocm_aiter_ops.is_enabled():\n        from aiter.ops.triton.moe_routing.routing import routing as aiter_routing\n        routing_data, gather_idx, scatter_idx = aiter_routing(gating_output, topk, sm_first=not renormalize)\n        return triton_kernel_fused_mxfp4_w4a8_experts(None, hidden_states, w1, w2, routing_data, gather_idx, scatter_idx, activation=activation.value, quant_config=quant_config, apply_router_weight_on_input=apply_router_weight_on_input, global_num_experts=global_num_experts, expert_map=expert_map, unpadded_N_w1=unpadded_N_w1, unpadded_K_w1=unpadded_K_w1, unpadded_N_w2=unpadded_N_w2, unpadded_K_w2=unpadded_K_w2)\n    if expert_map is not None:\n        from triton_kernels.topk import topk as topk_fn\n        sm_first = not renormalize\n        logits = gating_output\n        if sm_first:\n            logits = torch.softmax(logits, dim=-1)\n        topk_result = topk_fn(logits, topk, apply_softmax=not sm_first)\n        if isinstance(topk_result, tuple):\n            topk_weights, topk_ids_raw, _ = topk_result\n        else:\n            topk_weights = topk_result.vals\n            topk_ids_raw = topk_result.indx\n        topk_ids = expert_map[topk_ids_raw.to(torch.long)]\n        local_num_experts = w1.shape[0]\n        routing_data, gather_idx, scatter_idx = make_routing_data(topk_ids, topk_weights, local_num_experts)\n        effective_expert_map = None\n        effective_global_num_experts = local_num_experts\n    else:\n        routing_data, gather_idx, scatter_idx = legacy_routing(gating_output, topk, sm_first=not renormalize)\n        effective_expert_map = expert_map\n        effective_global_num_experts = global_num_experts\n    output = torch.empty_like(hidden_states)\n    effective_quant_config = quant_config if quant_config is not None else FUSED_MOE_UNQUANTIZED_CONFIG\n    return triton_kernel_fused_experts(output, hidden_states, w1, w2, routing_data, gather_idx, scatter_idx, topk=topk, activation=activation, quant_config=effective_quant_config, apply_router_weight_on_input=apply_router_weight_on_input, global_num_experts=effective_global_num_experts, expert_map=effective_expert_map)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/gpt_oss_triton_kernels_moe.py"
    },
    {
        "id": "triton_kernel_fused_experts",
        "coords": [
            13,
            3,
            3
        ],
        "fiber": 19,
        "logic": "def triton_kernel_fused_experts(output_tensor: torch.Tensor, hidden_states: torch.Tensor, w1, w2, routing_data, gather_indx, scatter_indx, topk: int, activation: MoEActivation=MoEActivation.SWIGLUOAI, quant_config: FusedMoEQuantConfig | None=None, swiglu_alpha: float=1.702, swiglu_limit: float=7.0, apply_router_weight_on_input: bool=False, global_num_experts: int=-1, expert_map: torch.Tensor | None=None, intermediate_cache: torch.Tensor | None=None, a1q_scale: torch.Tensor | None=None) -> torch.Tensor:\n    \"\"\"Triton implementation of fused expert computation using OAI kernels.\"\"\"\n    assert activation == MoEActivation.SWIGLUOAI, 'Only SWIGLUOAI activation is supported'\n    assert quant_config is not None\n    assert hidden_states.dtype == torch.bfloat16\n    assert quant_config.w1_bias is None or quant_config.w1_bias.dtype == torch.float32\n    assert quant_config.w2_bias is None or quant_config.w2_bias.dtype == torch.float32\n    assert hidden_states.ndim == 2\n    assert hidden_states.shape[-1] == w1.shape[-2]\n    assert w2.shape[-1] == w1.shape[1]\n    batch_dim = 1\n    M, K = hidden_states.shape[-2:]\n    E, _, N = w1.shape\n    if global_num_experts == -1:\n        global_num_experts = E\n    if intermediate_cache is None:\n        intermediate_cache = torch.empty((batch_dim, M * topk, N // 2), device=hidden_states.device, dtype=hidden_states.dtype)\n    intermediate_cache = _resize_cache(intermediate_cache, (batch_dim, M * topk, N // 2))\n    output_tensor = _resize_cache(output_tensor, (batch_dim, M, K))\n    act = FusedActivation(FnSpecs('swiglu', triton_kernels.swiglu.swiglu_fn, ('alpha', 'limit'), reduction_n=2), (swiglu_alpha, swiglu_limit)) if not use_legacy_triton_kernels else FusedActivation(FnSpecs('swiglu', triton_kernels.swiglu.swiglu_fn, ('alpha', 'limit')), (swiglu_alpha, swiglu_limit), 2)\n    gammas = routing_data.gate_scal if routing_data else None\n    matmul_ogs(hidden_states, w1, quant_config.w1_bias, routing_data, gather_indx=gather_indx, precision_config=quant_config.w1_precision, gammas=gammas if apply_router_weight_on_input else None, fused_activation=act, y=intermediate_cache)\n    matmul_ogs(intermediate_cache.view(M * topk, N // 2), w2, quant_config.w2_bias, routing_data, scatter_indx=scatter_indx, precision_config=quant_config.w2_precision, gammas=None if apply_router_weight_on_input else gammas, y=output_tensor)\n    output_tensor = output_tensor.view(M, K)\n    return output_tensor",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/gpt_oss_triton_kernels_moe.py"
    },
    {
        "id": "triton_kernel_fused_mxfp4_w4a8_experts",
        "coords": [
            17,
            13,
            15
        ],
        "fiber": 14,
        "logic": "def triton_kernel_fused_mxfp4_w4a8_experts(output_tensor: torch.Tensor, hidden_states: torch.Tensor, w1, w2, routing_data, gather_indx, scatter_indx, activation: str='silu', quant_config: FusedMoEQuantConfig | None=None, swiglu_alpha: float=1.702, swiglu_limit: float=7.0, apply_router_weight_on_input: bool=False, global_num_experts: int=-1, expert_map: torch.Tensor | None=None, a1q_scale: torch.Tensor | None=None, unpadded_N_w1=None, unpadded_K_w1=None, unpadded_N_w2=None, unpadded_K_w2=None) -> torch.Tensor:\n    assert quant_config is not None\n    assert hidden_states.dtype == torch.bfloat16\n    assert quant_config.w1_bias is None or quant_config.w1_bias.dtype == torch.float32\n    assert quant_config.w2_bias is None or quant_config.w2_bias.dtype == torch.float32\n    assert hidden_states.shape[-1] == w1.shape[-2]\n    assert w2.shape[-1] == w1.shape[1]\n    E, _, N = w1.shape\n    if global_num_experts == -1:\n        global_num_experts = E\n    gammas = routing_data.gate_scal if routing_data else None\n    from aiter.ops.triton.moe_op_gemm_a8w4 import moe_gemm_a8w4\n    from aiter.ops.triton.quant_moe import downcast_to_static_fp8\n    assert quant_config.w1_precision is not None, \"w1_precision in quant config can't be None\"\n    assert quant_config.w2_precision is not None, \"w2_precision in quant config can't be None\"\n    hidden_states = downcast_to_static_fp8(hidden_states, quant_config.w1_precision.flex_ctx.lhs_data.scale)\n    intermediate_cache1 = moe_gemm_a8w4(hidden_states, w1.storage.data, None, quant_config.w1_precision.weight_scale.storage.data, quant_config.w1_precision.flex_ctx.lhs_data.scale, quant_config.w2_precision.flex_ctx.lhs_data.scale, quant_config.w1_bias, routing_data, gather_indx=gather_indx, gammas=gammas if apply_router_weight_on_input else None, swizzle_mx_scale='CDNA4_SCALE', out_dtype=torch.float8_e4m3fn, apply_swiglu=True, alpha=swiglu_alpha, limit=swiglu_limit, unpadded_N=unpadded_N_w1, unpadded_K=unpadded_K_w1)\n    intermediate_cache3 = moe_gemm_a8w4(intermediate_cache1, w2.storage.data, None, quant_config.w2_precision.weight_scale.storage.data, quant_config.w2_precision.flex_ctx.lhs_data.scale, None, quant_config.w2_bias, routing_data, scatter_indx=scatter_indx, gammas=None if apply_router_weight_on_input else gammas, swizzle_mx_scale='CDNA4_SCALE', unpadded_N=unpadded_N_w2, unpadded_K=unpadded_K_w2)\n    return intermediate_cache3",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/gpt_oss_triton_kernels_moe.py"
    },
    {
        "id": "_setup_kernel",
        "coords": [
            25,
            30,
            0
        ],
        "fiber": 24,
        "logic": "def _setup_kernel(self, layer: Module, w13: torch.Tensor, w2: torch.Tensor) -> None:\n    w13, w2 = convert_to_unquantized_kernel_format(self.unquantized_backend, layer=layer, w13_weight=w13, w2_weight=w2)\n    replace_parameter(layer, 'w13_weight', w13)\n    replace_parameter(layer, 'w2_weight', w2)\n    self.moe_quant_config = self.get_fused_moe_quant_config(layer)\n    assert self.moe_quant_config is not None\n    assert self.experts_cls is not None\n    self.moe_kernel = make_unquantized_moe_kernel(quant_config=self.moe_quant_config, moe_config=self.moe, backend=self.unquantized_backend, experts_cls=self.experts_cls, routing_tables=layer._maybe_init_expert_routing_tables(), shared_experts=layer.shared_experts)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/unquantized_fused_moe_method.py"
    },
    {
        "id": "expert_triton_kernel",
        "coords": [
            11,
            11,
            26
        ],
        "fiber": 17,
        "logic": "@triton.jit\ndef expert_triton_kernel(a_ptr, b_ptr, c_ptr, expert_id, compute_type: tl.constexpr, M, N, K, a_scale_ptr, b_scale_ptr, b_zp_ptr, stride_am: tl.int64, stride_ak: tl.int64, stride_bk: tl.int64, stride_bn: tl.int64, stride_cm: tl.int64, stride_cn: tl.int64, stride_ase: tl.int64, stride_asm: tl.int64, stride_ask: tl.int64, stride_bse: tl.int64, stride_bsk: tl.int64, stride_bsn: tl.int64, offs_bn, group_n, group_k, use_fp8_w8a8: tl.constexpr, use_int8_w8a16: tl.constexpr, per_act_token_quant: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr):\n    offs_m = tl.arange(0, BLOCK_M)\n    offs_n = tl.arange(0, BLOCK_N) % N\n    offs_k = tl.arange(0, BLOCK_K)\n    mask_m = offs_m < M\n    a_ptrs = a_ptr + offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak\n    b_ptrs = b_ptr + offs_k[:, None] * stride_bk + offs_n[None, :] * stride_bn\n    accumulator = moe_mmk(a_ptrs, b_ptrs, K, expert_id, a_scale_ptr, b_scale_ptr, stride_ak, stride_bk, stride_ase, stride_asm, stride_ask, stride_bse, stride_bsk, stride_bsn, offs_m, offs_n, offs_bn, mask_m, group_n, group_k, BLOCK_M, BLOCK_N, BLOCK_K, compute_type, use_fp8_w8a8, use_int8_w8a16, per_act_token_quant)\n    offs_cn = tl.arange(0, BLOCK_N)\n    c_ptrs = c_ptr + offs_m[:, None] * stride_cm + offs_cn[None, :] * stride_cn\n    c_mask = mask_m[:, None] & (offs_cn[None, :] < N)\n    tl.store(c_ptrs, accumulator, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_batched_moe.py"
    },
    {
        "id": "batched_triton_kernel",
        "coords": [
            14,
            14,
            27
        ],
        "fiber": 24,
        "logic": "@triton.jit\ndef batched_triton_kernel(a_ptr, b_ptr, c_ptr, expert_num_tokens, compute_type: tl.constexpr, max_num_tokens, K, N, a_scale_ptr, b_scale_ptr, b_zp_ptr, stride_ae: tl.int64, stride_am: tl.int64, stride_ak: tl.int64, stride_be: tl.int64, stride_bk: tl.int64, stride_bn: tl.int64, stride_ce: tl.int64, stride_cm: tl.int64, stride_cn: tl.int64, stride_ase: tl.int64, stride_asm: tl.int64, stride_ask: tl.int64, stride_bse: tl.int64, stride_bsk: tl.int64, stride_bsn: tl.int64, group_n: tl.constexpr, group_k: tl.constexpr, use_fp8_w8a8: tl.constexpr, use_int8_w8a16: tl.constexpr, per_act_token_quant: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr):\n    expert_id = tl.program_id(axis=0)\n    e_num_tokens = tl.load(expert_num_tokens + expert_id)\n    if e_num_tokens == 0:\n        return\n    pid_mn = tl.program_id(axis=1)\n    num_pid_n = tl.cdiv(N, BLOCK_N)\n    pid_m = pid_mn // num_pid_n\n    pid_n = pid_mn % num_pid_n\n    cta_m_start = pid_m * BLOCK_M\n    cta_n_start = pid_n * BLOCK_N\n    if cta_m_start >= e_num_tokens:\n        return\n    cta_m_size = min(BLOCK_M, e_num_tokens - cta_m_start)\n    cta_n_size = min(BLOCK_N, N - cta_n_start)\n    a_ptr = a_ptr + expert_id * stride_ae + cta_m_start * stride_am\n    b_ptr = b_ptr + expert_id * stride_be + cta_n_start * stride_bn\n    c_ptr = c_ptr + expert_id * stride_ce + cta_m_start * stride_cm + cta_n_start * stride_cn\n    offs_bn = (pid_n * BLOCK_N + tl.arange(0, BLOCK_N).to(tl.int64)) % N\n    if use_fp8_w8a8:\n        a_scale_ptr = a_scale_ptr + expert_id * stride_ase\n        b_scale_ptr = b_scale_ptr + expert_id * stride_bse\n        if group_k > 0 and group_n > 0 or per_act_token_quant:\n            a_scale_ptr = a_scale_ptr + cta_m_start * stride_asm\n    expert_triton_kernel(a_ptr, b_ptr, c_ptr, expert_id, compute_type, cta_m_size, cta_n_size, K, a_scale_ptr, b_scale_ptr, b_zp_ptr, stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn, stride_ase, stride_asm, stride_ask, stride_bse, stride_bsk, stride_bsn, offs_bn, group_n, group_k, use_fp8_w8a8, use_int8_w8a16, per_act_token_quant, BLOCK_M, BLOCK_N, BLOCK_K)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_batched_moe.py"
    },
    {
        "id": "invoke_moe_batched_triton_kernel",
        "coords": [
            11,
            12,
            6
        ],
        "fiber": 29,
        "logic": "def invoke_moe_batched_triton_kernel(A: torch.Tensor, B: torch.Tensor, C: torch.Tensor, expert_num_tokens: torch.Tensor, compute_type: tl.dtype, A_scale: torch.Tensor | None, B_scale: torch.Tensor | None, B_zp: torch.Tensor, use_fp8_w8a8: bool, use_int8_w8a16: bool, use_int4_w4a16: bool, config: dict[str, int], per_act_token_quant: bool, block_shape: list[int] | None=None):\n    assert not use_int4_w4a16\n    max_num_tokens = A.size(1)\n    K = A.size(2)\n    N = C.size(2)\n    BLOCK_M = config['BLOCK_SIZE_M']\n    BLOCK_N = config['BLOCK_SIZE_N']\n    BLOCK_K = config['BLOCK_SIZE_K']\n    grid = (expert_num_tokens.size(0), triton.cdiv(max_num_tokens, BLOCK_M) * triton.cdiv(B.size(1), BLOCK_N))\n    A_scale = normalize_batched_scales_shape(A_scale, expert_num_tokens.shape[0])\n    if B_scale is not None and B_scale.ndim == 1:\n        assert B_scale.numel() == expert_num_tokens.shape[0]\n        B_scale = B_scale.view(-1, 1, 1)\n    assert A_scale is None or A_scale.ndim == 3, f'{(0 if A_scale is None else A_scale.shape)}'\n    assert B_scale is None or B_scale.ndim == 1 or B_scale.ndim == 3, f'{(0 if B_scale is None else B_scale.shape)}'\n    if B_scale is not None:\n        if B_scale.ndim == 1:\n            stride_bse = 1\n            stride_bsk = 0\n            stride_bsn = 0\n        else:\n            stride_bse = B_scale.stride(0)\n            stride_bsk = B_scale.stride(2)\n            stride_bsn = B_scale.stride(1)\n    else:\n        stride_bse = 0\n        stride_bsk = 0\n        stride_bsn = 0\n    if A_scale is not None:\n        stride_ase = A_scale.stride(0)\n        stride_asm = A_scale.stride(1)\n        stride_ask = A_scale.stride(2)\n    else:\n        stride_ase = 0\n        stride_asm = 0\n        stride_ask = 0\n    batched_triton_kernel[grid](A, B, C, expert_num_tokens, compute_type, max_num_tokens, K, N, A_scale, B_scale, B_zp, A.stride(0), A.stride(1), A.stride(2), B.stride(0), B.stride(2), B.stride(1), C.stride(0), C.stride(1), C.stride(2), stride_ase, stride_asm, stride_ask, stride_bse, stride_bsk, stride_bsn, 0 if block_shape is None else block_shape[0], 0 if block_shape is None else block_shape[1], use_fp8_w8a8, use_int8_w8a16, per_act_token_quant, BLOCK_M=BLOCK_M, BLOCK_N=BLOCK_N, BLOCK_K=BLOCK_K)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_batched_moe.py"
    },
    {
        "id": "batched_moe_kernel_quantize_input",
        "coords": [
            17,
            14,
            0
        ],
        "fiber": 0,
        "logic": "def batched_moe_kernel_quantize_input(A: torch.Tensor, A_scale: torch.Tensor | None, num_tokens: int, E: int, N: int, expert_num_tokens: torch.Tensor, qtype: torch.dtype | None, per_act_token_quant: bool, block_shape: list[int] | None=None) -> tuple[torch.Tensor, torch.Tensor | None]:\n    if torch.compiler.is_compiling() or torch.cuda.is_current_stream_capturing():\n        hidden_dim = A.size(-1)\n        assert A_scale is None or A_scale.ndim <= 2, f'{(A_scale.shape if A_scale is not None else None)}'\n        A_q, A_q_scale = moe_kernel_quantize_input(A.view(-1, hidden_dim), A_scale, qtype, per_act_token_quant, block_shape)\n        A_q = A_q.view(E, -1, hidden_dim)\n        A_q_scale = normalize_batched_scales_shape(A_q_scale, E)\n        return (A_q, A_q_scale)\n    elif qtype is None:\n        return (A, normalize_batched_scales_shape(A_scale, E))\n    else:\n        A_q = torch.empty_like(A, dtype=qtype)\n        if per_act_token_quant:\n            assert block_shape is None\n            scale_shape = (E, num_tokens, 1)\n        elif block_shape is not None:\n            _, block_k = block_shape\n            k_tiles = (A.shape[-1] + block_k - 1) // block_k\n            scale_shape = (E, num_tokens, k_tiles)\n        else:\n            scale_shape = (E, 1, 1)\n        A_q_scale = torch.zeros(scale_shape, dtype=torch.float32, device=A.device)\n        num_experts = expert_num_tokens.numel()\n        A_scale = normalize_batched_scales_shape(A_scale, num_experts)\n        for e in range(E):\n            num_tokens = int(expert_num_tokens[e].item())\n            if num_tokens > 0:\n                if A_scale is not None:\n                    scales = A_scale[e, :min(num_tokens, A_scale.shape[1])]\n                else:\n                    scales = None\n                A_q[e, :num_tokens], tmp_scale = moe_kernel_quantize_input(A[e, :num_tokens], scales, qtype, per_act_token_quant, block_shape)\n                assert tmp_scale is not None\n                A_q_scale[e, :tmp_scale.shape[0]] = tmp_scale\n        return (A_q, A_q_scale)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_batched_moe.py"
    },
    {
        "id": "use_all2all_kernels",
        "coords": [
            0,
            12,
            13
        ],
        "fiber": 25,
        "logic": "@property\ndef use_all2all_kernels(self):\n    return self.dp_size > 1 and self.use_ep",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_deepep_ht_kernels",
        "coords": [
            27,
            16,
            24
        ],
        "fiber": 5,
        "logic": "@property\ndef use_deepep_ht_kernels(self):\n    return self.use_all2all_kernels and self.all2all_backend == 'deepep_high_throughput'",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_deepep_ll_kernels",
        "coords": [
            3,
            4,
            28
        ],
        "fiber": 4,
        "logic": "@property\ndef use_deepep_ll_kernels(self):\n    return self.use_all2all_kernels and self.all2all_backend == 'deepep_low_latency'",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_fi_nvl_two_sided_kernels",
        "coords": [
            5,
            11,
            4
        ],
        "fiber": 20,
        "logic": "@property\ndef use_fi_nvl_two_sided_kernels(self):\n    return self.use_all2all_kernels and (self.all2all_backend == 'flashinfer_all2allv' or self.all2all_backend == 'flashinfer_nvlink_two_sided')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_fi_nvl_one_sided_kernels",
        "coords": [
            24,
            12,
            1
        ],
        "fiber": 6,
        "logic": "@property\ndef use_fi_nvl_one_sided_kernels(self):\n    return self.use_all2all_kernels and self.all2all_backend == 'flashinfer_nvlink_one_sided'",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_ag_rs_all2all_kernels",
        "coords": [
            29,
            2,
            12
        ],
        "fiber": 12,
        "logic": "@property\ndef use_ag_rs_all2all_kernels(self):\n    return self.use_all2all_kernels and self.all2all_backend == 'allgather_reducescatter'",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_mori_kernels",
        "coords": [
            20,
            7,
            10
        ],
        "fiber": 6,
        "logic": "@property\ndef use_mori_kernels(self):\n    return self.use_all2all_kernels and self.all2all_backend == 'mori'",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_nixl_ep_kernels",
        "coords": [
            17,
            29,
            10
        ],
        "fiber": 25,
        "logic": "@property\ndef use_nixl_ep_kernels(self):\n    return self.use_all2all_kernels and self.all2all_backend == 'nixl_ep'",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_deepep_ht_kernels",
        "coords": [
            27,
            16,
            24
        ],
        "fiber": 5,
        "logic": "@property\ndef use_deepep_ht_kernels(self):\n    return self.moe_parallel_config.use_deepep_ht_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_deepep_ll_kernels",
        "coords": [
            3,
            4,
            28
        ],
        "fiber": 4,
        "logic": "@property\ndef use_deepep_ll_kernels(self):\n    return self.moe_parallel_config.use_deepep_ll_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_mori_kernels",
        "coords": [
            20,
            7,
            10
        ],
        "fiber": 6,
        "logic": "@property\ndef use_mori_kernels(self):\n    return self.moe_parallel_config.use_mori_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_fi_nvl_two_sided_kernels",
        "coords": [
            5,
            11,
            4
        ],
        "fiber": 20,
        "logic": "@property\ndef use_fi_nvl_two_sided_kernels(self):\n    return self.moe_parallel_config.use_fi_nvl_two_sided_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_fi_nvl_one_sided_kernels",
        "coords": [
            24,
            12,
            1
        ],
        "fiber": 6,
        "logic": "@property\ndef use_fi_nvl_one_sided_kernels(self):\n    return self.moe_parallel_config.use_fi_nvl_one_sided_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_ag_rs_all2all_kernels",
        "coords": [
            29,
            2,
            12
        ],
        "fiber": 12,
        "logic": "@property\ndef use_ag_rs_all2all_kernels(self):\n    return self.moe_parallel_config.use_ag_rs_all2all_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "use_nixl_ep_kernels",
        "coords": [
            17,
            29,
            10
        ],
        "fiber": 25,
        "logic": "@property\ndef use_nixl_ep_kernels(self):\n    return self.moe_parallel_config.use_nixl_ep_kernels",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/config.py"
    },
    {
        "id": "_fwd_kernel_ep_scatter_1",
        "coords": [
            14,
            3,
            3
        ],
        "fiber": 20,
        "logic": "@triton.jit\ndef _fwd_kernel_ep_scatter_1(num_recv_tokens_per_expert, expert_start_loc, m_indices, num_experts: tl.constexpr, BLOCK_E: tl.constexpr, BLOCK_EXPERT_NUM: tl.constexpr):\n    cur_expert = tl.program_id(0)\n    offset_cumsum = tl.arange(0, BLOCK_EXPERT_NUM)\n    tokens_per_expert = tl.load(num_recv_tokens_per_expert + offset_cumsum, mask=offset_cumsum < num_experts, other=0)\n    tokens_per_expert = round_up_128(tokens_per_expert)\n    cumsum = tl.cumsum(tokens_per_expert) - tokens_per_expert\n    cur_expert_start = tl.sum(tl.where(offset_cumsum == cur_expert, cumsum, tl.zeros_like(cumsum)))\n    tl.store(expert_start_loc + cur_expert, cur_expert_start)\n    cur_expert_token_num = tl.load(num_recv_tokens_per_expert + cur_expert)\n    m_indices_start_ptr = m_indices + cur_expert_start\n    off_expert = tl.arange(0, BLOCK_E)\n    for start_m in tl.range(0, cur_expert_token_num, BLOCK_E):\n        offs = start_m + off_expert\n        mask = offs < cur_expert_token_num\n        tl.store(m_indices_start_ptr + offs, cur_expert, mask=mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/deep_gemm_utils.py"
    },
    {
        "id": "_fwd_kernel_ep_scatter_2",
        "coords": [
            2,
            29,
            3
        ],
        "fiber": 3,
        "logic": "@triton.jit\ndef _fwd_kernel_ep_scatter_2(total_token_num, expert_start_loc, recv_x, recv_x_stride0, recv_x_stride1, recv_x_scale, recv_x_scale_stride0, recv_x_scale_stride1, recv_topk, recv_topk_stride0, recv_topk_stride1, output_tensor, output_tensor_stride0, output_tensor_stride1, output_tensor_scale, output_tensor_scale_stride0, output_tensor_scale_stride1, output_index, output_index_stride0, output_index_stride1, topk_num: tl.constexpr, expert_map, HAS_EXPERT_MAP: tl.constexpr, HIDDEN_SIZE: tl.constexpr, HIDDEN_SIZE_PAD: tl.constexpr, SCALE_HIDDEN_SIZE: tl.constexpr, SCALE_HIDDEN_SIZE_PAD: tl.constexpr):\n    start_token_id = tl.program_id(0)\n    grid_num = tl.num_programs(0)\n    offset_in = tl.arange(0, HIDDEN_SIZE_PAD)\n    mask = offset_in < HIDDEN_SIZE\n    offset_in_s = tl.arange(0, SCALE_HIDDEN_SIZE_PAD)\n    mask_s = offset_in_s < SCALE_HIDDEN_SIZE\n    for token_id in range(start_token_id, total_token_num, grid_num):\n        to_copy = tl.load(recv_x + token_id * recv_x_stride0 + offset_in, mask=mask)\n        to_copy_s = tl.load(recv_x_scale + token_id * recv_x_scale_stride0 + offset_in_s, mask=mask_s)\n        for topk_index in tl.range(0, topk_num, 1, num_stages=4):\n            expert_id = tl.load(recv_topk + token_id * recv_topk_stride0 + topk_index)\n            if HAS_EXPERT_MAP:\n                expert_id = apply_expert_map(expert_id, expert_map)\n            if expert_id >= 0:\n                dest_token_index = tl.atomic_add(expert_start_loc + expert_id, 1)\n                tl.store(output_index + token_id * output_index_stride0 + topk_index, dest_token_index)\n                output_tensor_ptr = output_tensor + dest_token_index * output_tensor_stride0\n                output_tensor_scale_ptr = output_tensor_scale + dest_token_index * output_tensor_scale_stride0\n                tl.store(output_tensor_ptr + offset_in, to_copy, mask=mask)\n                tl.store(output_tensor_scale_ptr + offset_in_s, to_copy_s, mask=mask_s)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/deep_gemm_utils.py"
    },
    {
        "id": "_fwd_kernel_ep_gather",
        "coords": [
            6,
            19,
            9
        ],
        "fiber": 3,
        "logic": "@triton.jit\ndef _fwd_kernel_ep_gather(total_token_num, input_tensor, input_tensor_stride0, input_tensor_stride1, recv_topk_ids, recv_topk_ids_stride0, recv_topk_ids_stride1, recv_topk_weight, recv_topk_weight_stride0, recv_topk_weight_stride1, input_index, input_index_stride0, input_index_stride1, output_tensor, output_tensor_stride0, output_tensor_stride1, topk_num: tl.constexpr, expert_map, HAS_EXPERT_MAP: tl.constexpr, BLOCK_D: tl.constexpr):\n    cur_block = tl.program_id(0)\n    start_cur_token = tl.program_id(1)\n    grid_num = tl.num_programs(1)\n    for cur_token in range(start_cur_token, total_token_num, grid_num):\n        off_d = tl.arange(0, BLOCK_D)\n        accumulator = tl.zeros([BLOCK_D], dtype=tl.float32)\n        for topk_index in range(0, topk_num):\n            expert_id = tl.load(recv_topk_ids + cur_token * recv_topk_ids_stride0 + topk_index)\n            if HAS_EXPERT_MAP:\n                expert_id = apply_expert_map(expert_id, expert_map)\n            if expert_id >= 0:\n                source_token_index = tl.load(input_index + cur_token * input_index_stride0 + topk_index)\n                acc_weight = tl.load(recv_topk_weight + cur_token * recv_topk_weight_stride0 + topk_index)\n                tmp = tl.load(input_tensor + source_token_index * input_tensor_stride0 + cur_block * BLOCK_D + off_d)\n                accumulator += tmp.to(tl.float32) * acc_weight\n        tl.store(output_tensor + cur_token * output_tensor_stride0 + cur_block * BLOCK_D + off_d, accumulator.to(output_tensor.dtype.element_ty))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/deep_gemm_utils.py"
    },
    {
        "id": "moe_kernel_quantize_input",
        "coords": [
            20,
            30,
            28
        ],
        "fiber": 16,
        "logic": "def moe_kernel_quantize_input(A: torch.Tensor, A_scale: torch.Tensor | None, quant_dtype: None | torch.dtype | str, per_act_token_quant: bool, block_shape: list[int] | None=None, is_fp4_scale_swizzled: bool=True, ocp_mx_scheme: str | None=None) -> tuple[torch.Tensor, torch.Tensor | None]:\n    if ocp_mx_scheme is not None:\n        if ocp_mx_scheme in {'w_mxfp4', 'w_mxfp4_a_mxfp4'}:\n            pass\n        elif ocp_mx_scheme.endswith('a_fp8'):\n            qA, qA_scale = ops.scaled_fp8_quant(A, A_scale, use_per_token_if_dynamic=False)\n            A = per_tensor_dequantize(qA, qA_scale).to(A.dtype)\n            return (A, None)\n    if quant_dtype == current_platform.fp8_dtype():\n        return _fp8_quantize(A, A_scale, per_act_token_quant, block_shape)\n    elif quant_dtype == torch.int8:\n        return _int8_quantize(A, A_scale, per_act_token_quant, block_shape)\n    elif quant_dtype == 'nvfp4':\n        return _nvfp4_quantize(A, A_scale, is_sf_swizzled_layout=is_fp4_scale_swizzled)\n    elif quant_dtype == 'mxfp4':\n        return _mxfp4_quantize(A, A_scale, per_act_token_quant, block_shape)\n    elif quant_dtype == 'mxfp8':\n        return _mxfp8_e4m3_quantize(A, A_scale, per_act_token_quant, block_shape, is_sf_swizzled_layout=is_fp4_scale_swizzled)\n    elif quant_dtype == 'mxfp6_e3m2':\n        return _mxfp6_e3m2_quantize(A, A_scale, per_act_token_quant, block_shape)\n    elif quant_dtype == 'mxfp6_e2m3':\n        return _mxfp6_e2m3_quantize(A, A_scale, per_act_token_quant, block_shape)\n    else:\n        return (A, A_scale)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/utils.py"
    },
    {
        "id": "maybe_init_modular_kernel",
        "coords": [
            14,
            27,
            29
        ],
        "fiber": 8,
        "logic": "def maybe_init_modular_kernel(self) -> None:\n    if self.quant_method.supports_internal_mk or self.quant_method.is_monolithic:\n        return None\n    self.ensure_moe_quant_config_init()\n    routing_tables = self._maybe_init_expert_routing_tables()\n    prepare_finalize = self.base_quant_method.maybe_make_prepare_finalize(routing_tables=routing_tables)\n    if prepare_finalize is not None:\n        logger.debug('%s for %s(%s)', prepare_finalize.__class__.__name__, self, id(self))\n        self._replace_quant_method(FusedMoEModularMethod.make(self, self.base_quant_method, prepare_finalize, self.shared_experts, inplace=not self.moe_config.disable_inplace))",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/layer.py"
    },
    {
        "id": "maybe_all_reduce_tensor_model_parallel",
        "coords": [
            22,
            21,
            15
        ],
        "fiber": 27,
        "logic": "def maybe_all_reduce_tensor_model_parallel(self, final_hidden_states: torch.Tensor):\n    \"\"\"\n        Some combine kernels reduce across GPU ranks by default.\n        \"\"\"\n    return self.runner.maybe_all_reduce_tensor_model_parallel(final_hidden_states)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/layer.py"
    },
    {
        "id": "fused_moe_kernel_gptq_awq",
        "coords": [
            17,
            5,
            23
        ],
        "fiber": 14,
        "logic": "@triton.jit\ndef fused_moe_kernel_gptq_awq(a_ptr, b_ptr, c_ptr, b_scale_ptr, b_zp_ptr, topk_weights_ptr, sorted_token_ids_ptr, expert_ids_ptr, num_tokens_post_padded_ptr, N: tl.constexpr, K: tl.constexpr, EM, num_valid_tokens, stride_am, stride_ak, stride_be, stride_bk, stride_bn, stride_cm, stride_cn, stride_bse, stride_bsk, stride_bsn, stride_bze, stride_bzk, stride_bzn, block_k_diviable: tl.constexpr, group_size: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, GROUP_SIZE_M: tl.constexpr, SPLIT_K: tl.constexpr, MUL_ROUTED_WEIGHT: tl.constexpr, top_k: tl.constexpr, compute_type: tl.constexpr, has_zp: tl.constexpr, use_int4_w4a16: tl.constexpr, use_int8_w8a16: tl.constexpr):\n    \"\"\"\n    Implements the fused computation for a Mixture of Experts (MOE) using\n    token and expert matrices.\n\n    Key Parameters:\n    - A: The input tensor representing tokens with shape (*, K), where '*' can\n        be any shape representing batches and K is the feature dimension of\n        each token.\n    - B: The stacked MOE weight tensor with shape (E, N, K), where E is\n        the number of experts, K is the input feature dimension, and N is\n        the output feature dimension.\n    - C: The output cache tensor with shape (M, topk, N), where M is the\n        total number of tokens post padding, topk is the number of times\n        each token is repeated, and N is the output feature dimension.\n    - sorted_token_ids: A tensor containing the sorted indices of tokens,\n        repeated topk times and arranged by the expert index they are\n        assigned to.\n    - expert_ids: A tensor containing the indices of the expert for each\n        block. It determines which expert matrix from B should be used for\n        each block in A.\n    This kernel performs the multiplication of a token by its corresponding\n    expert matrix as determined by `expert_ids`. The sorting of\n    `sorted_token_ids` by expert index and padding ensures divisibility by\n    BLOCK_SIZE_M, which is necessary to maintain consistency in block matrix\n    multiplication across different blocks processed by the same expert.\n    \"\"\"\n    pid = tl.program_id(axis=0)\n    num_pid_m = tl.cdiv(EM, BLOCK_SIZE_M)\n    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)\n    num_pid_in_group = GROUP_SIZE_M * num_pid_n\n    group_id = pid // num_pid_in_group\n    first_pid_m = group_id * GROUP_SIZE_M\n    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)\n    pid_m = first_pid_m + pid % num_pid_in_group % group_size_m\n    pid_n = pid % num_pid_in_group // group_size_m\n    num_tokens_post_padded = tl.load(num_tokens_post_padded_ptr)\n    if pid_m * BLOCK_SIZE_M >= num_tokens_post_padded:\n        return\n    offs_token_id = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M).to(tl.int64)\n    offs_token = tl.load(sorted_token_ids_ptr + offs_token_id).to(tl.int64)\n    token_mask = offs_token < num_valid_tokens\n    off_experts = tl.load(expert_ids_ptr + pid_m).to(tl.int64)\n    if off_experts == -1:\n        write_zeros_to_output(c_ptr, stride_cm, stride_cn, pid_n, N, offs_token, token_mask, BLOCK_SIZE_M, BLOCK_SIZE_N, compute_type)\n        return\n    offs_bn = (pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N).to(tl.int64)) % N\n    offs_k = tl.arange(0, BLOCK_SIZE_K)\n    a_ptrs = a_ptr + (offs_token[:, None] // top_k * stride_am + offs_k[None, :] * stride_ak)\n    if use_int4_w4a16:\n        b_ptrs = b_ptr + off_experts * stride_be + offs_k[:, None] // 2 * stride_bk + offs_bn[None, :] * stride_bn\n        b_shifter = offs_k[:, None] % 2 * 4\n    elif use_int8_w8a16:\n        b_ptrs = b_ptr + off_experts * stride_be + offs_k[:, None] * stride_bk + offs_bn[None, :] * stride_bn\n    if not has_zp and use_int4_w4a16:\n        b_zp_num = 8\n    if not has_zp and use_int8_w8a16:\n        b_zp_num = 128\n    elif has_zp and use_int4_w4a16:\n        b_zp_shifter = offs_bn[None, :] % 2 * 4\n    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K)):\n        if not block_k_diviable:\n            k_mask = offs_k[:, None] < K - k * BLOCK_SIZE_K\n            k_other = 0.0\n        else:\n            k_mask = None\n            k_other = None\n        a = tl.load(a_ptrs, mask=token_mask[:, None] & (offs_k[None, :] < K - k * BLOCK_SIZE_K), other=0.0)\n        b = tl.load(b_ptrs)\n        if use_int4_w4a16:\n            b = b >> b_shifter & 15\n        b_scale_ptrs = b_scale_ptr + off_experts * stride_bse + offs_bn[None, :] * stride_bsn + (offs_k[:, None] + BLOCK_SIZE_K * k) // group_size * stride_bsk\n        b_scale = tl.load(b_scale_ptrs, mask=k_mask, other=k_other)\n        b_scale = b_scale.to(tl.float32)\n        if has_zp and use_int4_w4a16:\n            offs_k_true = (offs_k[:, None] + BLOCK_SIZE_K * k) // group_size\n            b_zp_ptrs = b_zp_ptr + off_experts * stride_bze + offs_bn[None, :] // 2 * stride_bzn + offs_k_true * stride_bzk\n            b_zp = tl.load(b_zp_ptrs, mask=k_mask, other=k_other)\n            b_zp = b_zp >> b_zp_shifter & 15\n            b_zp = b_zp.to(tl.float32)\n        elif has_zp and use_int8_w8a16:\n            offs_k_true = (offs_k[:, None] + BLOCK_SIZE_K * k) // group_size\n            b_zp_ptrs = b_zp_ptr + off_experts * stride_bze + offs_bn[None, :] * stride_bzn + offs_k_true * stride_bzk\n            b_zp = tl.load(b_zp_ptrs, mask=k_mask, other=k_other)\n            b_zp = b_zp.to(tl.float32)\n        if has_zp:\n            b = ((b.to(tl.float32) - b_zp) * b_scale).to(compute_type)\n        else:\n            b = ((b.to(tl.float32) - b_zp_num) * b_scale).to(compute_type)\n        accumulator = tl.dot(a, b, acc=accumulator)\n        a_ptrs += BLOCK_SIZE_K * stride_ak\n        if use_int4_w4a16:\n            b_ptrs += BLOCK_SIZE_K // 2 * stride_bk\n        else:\n            b_ptrs += BLOCK_SIZE_K * stride_bk\n    if MUL_ROUTED_WEIGHT:\n        moe_weight = tl.load(topk_weights_ptr + offs_token, mask=token_mask, other=0)\n        accumulator = accumulator * moe_weight[:, None]\n    accumulator = accumulator.to(compute_type)\n    offs_cn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    c_ptrs = c_ptr + stride_cm * offs_token[:, None] + stride_cn * offs_cn[None, :]\n    c_mask = token_mask[:, None] & (offs_cn[None, :] < N)\n    tl.store(c_ptrs, accumulator, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "fused_moe_kernel",
        "coords": [
            19,
            25,
            8
        ],
        "fiber": 21,
        "logic": "@triton.jit\ndef fused_moe_kernel(a_ptr, b_ptr, c_ptr, b_bias_ptr, a_scale_ptr, b_scale_ptr, topk_weights_ptr, sorted_token_ids_ptr, expert_ids_ptr, num_tokens_post_padded_ptr, N, K, EM, num_valid_tokens, stride_am, stride_ak, stride_be, stride_bk, stride_bn, stride_cm, stride_cn, stride_asm, stride_ask, stride_bse, stride_bsk, stride_bsn, stride_bbe, stride_bbn, group_n: tl.constexpr, group_k: tl.constexpr, naive_block_assignment: tl.constexpr, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr, GROUP_SIZE_M: tl.constexpr, SPLIT_K: tl.constexpr, MUL_ROUTED_WEIGHT: tl.constexpr, top_k: tl.constexpr, compute_type: tl.constexpr, use_fp8_w8a8: tl.constexpr, use_int8_w8a8: tl.constexpr, use_int8_w8a16: tl.constexpr, per_channel_quant: tl.constexpr, HAS_BIAS: tl.constexpr):\n    \"\"\"\n    Implements the fused computation for a Mixture of Experts (MOE) using\n    token and expert matrices.\n\n    Key Parameters:\n    - A: The input tensor representing tokens with shape (*, K), where '*' can\n        be any shape representing batches and K is the feature dimension of\n        each token.\n    - B: The stacked MOE weight tensor with shape (E, N, K), where E is\n        the number of experts, K is the input feature dimension, and N is\n        the output feature dimension.\n    - C: The output cache tensor with shape (M, topk, N), where M is the\n        total number of tokens post padding, topk is the number of times\n        each token is repeated, and N is the output feature dimension.\n    - sorted_token_ids: A tensor containing the sorted indices of tokens,\n        repeated topk times and arranged by the expert index they are\n        assigned to.\n    - expert_ids: A tensor containing the indices of the expert for each\n        block. It determines which expert matrix from B should be used for\n        each block in A.\n    - naive_block_assignment: A boolean flag indicating whether to use naive\n        token wise block assignment. If True, each block corresponds to a\n        single token.\n    This kernel performs the multiplication of a token by its corresponding\n    expert matrix as determined by `expert_ids`. The sorting of\n    `sorted_token_ids` by expert index and padding ensures divisibility by\n    BLOCK_SIZE_M, which is necessary to maintain consistency in block matrix\n    multiplication across different blocks processed by the same expert.\n    \"\"\"\n    pid = tl.program_id(axis=0)\n    num_pid_m = tl.cdiv(EM, BLOCK_SIZE_M)\n    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)\n    num_pid_in_group = GROUP_SIZE_M * num_pid_n\n    group_id = pid // num_pid_in_group\n    first_pid_m = group_id * GROUP_SIZE_M\n    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)\n    pid_m = first_pid_m + pid % num_pid_in_group % group_size_m\n    pid_n = pid % num_pid_in_group // group_size_m\n    offs = tl.arange(0, BLOCK_SIZE_M).to(tl.int64)\n    num_tokens_post_padded = tl.load(num_tokens_post_padded_ptr)\n    if pid_m * BLOCK_SIZE_M >= num_tokens_post_padded:\n        return\n    if not naive_block_assignment:\n        offs_token_id = pid_m * BLOCK_SIZE_M + offs\n        offs_token = tl.load(sorted_token_ids_ptr + offs_token_id)\n    else:\n        offs_token = tl.where(offs == 0, pid_m, num_valid_tokens)\n    offs_token = offs_token.to(tl.int64)\n    token_mask = offs_token < num_valid_tokens\n    off_experts = tl.load(expert_ids_ptr + pid_m).to(tl.int64)\n    if off_experts == -1:\n        write_zeros_to_output(c_ptr, stride_cm, stride_cn, pid_n, N, offs_token, token_mask, BLOCK_SIZE_M, BLOCK_SIZE_N, compute_type)\n        return\n    offs_bn = (pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N).to(tl.int64)) % N\n    offs_k = tl.arange(0, BLOCK_SIZE_K)\n    a_ptrs = a_ptr + (offs_token[:, None] // top_k * stride_am + offs_k[None, :] * stride_ak)\n    b_ptrs = b_ptr + off_experts * stride_be + (offs_k[:, None] * stride_bk + offs_bn[None, :] * stride_bn)\n    if use_int8_w8a16:\n        b_scale_ptrs = b_scale_ptr + off_experts * stride_bse + offs_bn[None, :] * stride_bsn\n        b_scale = tl.load(b_scale_ptrs)\n    if use_fp8_w8a8 or use_int8_w8a8:\n        if group_k > 0 and group_n > 0:\n            a_scale_ptrs = a_scale_ptr + offs_token // top_k * stride_asm\n            offs_bsn = offs_bn // group_n\n            b_scale_ptrs = b_scale_ptr + off_experts * stride_bse + offs_bsn * stride_bsn\n        elif per_channel_quant:\n            b_scale_ptrs = b_scale_ptr + off_experts * stride_bse + offs_bn[None, :] * stride_bsn\n            b_scale = tl.load(b_scale_ptrs)\n            a_scale_ptrs = a_scale_ptr + offs_token // top_k * stride_asm\n            a_scale = tl.load(a_scale_ptrs, mask=token_mask, other=0.0)[:, None]\n        else:\n            a_scale = tl.load(a_scale_ptr)\n            b_scale = tl.load(b_scale_ptr + off_experts)\n    if HAS_BIAS:\n        bias_ptrs = b_bias_ptr + off_experts * stride_bbe + offs_bn * stride_bbn\n        bias = tl.load(bias_ptrs, mask=offs_bn < N, other=0.0)\n    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)\n    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K)):\n        a = tl.load(a_ptrs, mask=token_mask[:, None] & (offs_k[None, :] < K - k * BLOCK_SIZE_K), other=0.0)\n        b = tl.load(b_ptrs, mask=offs_k[:, None] < K - k * BLOCK_SIZE_K, other=0.0)\n        if use_int8_w8a16:\n            accumulator = tl.dot(a, b.to(compute_type), acc=accumulator)\n        elif use_fp8_w8a8 or use_int8_w8a8:\n            if group_k > 0 and group_n > 0:\n                k_start = k * BLOCK_SIZE_K\n                offs_ks = k_start // group_k\n                a_scale = tl.load(a_scale_ptrs + offs_ks * stride_ask, mask=token_mask, other=0.0)\n                b_scale = tl.load(b_scale_ptrs + offs_ks * stride_bsk)\n                accumulator += tl.dot(a, b) * a_scale[:, None] * b_scale[None, :]\n            elif use_fp8_w8a8:\n                accumulator = tl.dot(a, b, acc=accumulator)\n            else:\n                accumulator += tl.dot(a, b)\n        else:\n            accumulator += tl.dot(a, b)\n        a_ptrs += BLOCK_SIZE_K * stride_ak\n        b_ptrs += BLOCK_SIZE_K * stride_bk\n    if use_int8_w8a16:\n        accumulator = accumulator * b_scale\n    elif (use_fp8_w8a8 or use_int8_w8a8) and (not (group_k > 0 and group_n > 0)):\n        accumulator = accumulator * a_scale * b_scale\n    if HAS_BIAS:\n        accumulator += bias[None, :]\n    if MUL_ROUTED_WEIGHT:\n        moe_weight = tl.load(topk_weights_ptr + offs_token, mask=token_mask, other=0)\n        accumulator *= moe_weight[:, None]\n    accumulator = accumulator.to(compute_type)\n    offs_cn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)\n    c_ptrs = c_ptr + stride_cm * offs_token[:, None] + stride_cn * offs_cn[None, :]\n    c_mask = token_mask[:, None] & (offs_cn[None, :] < N)\n    tl.store(c_ptrs, accumulator, mask=c_mask)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "invoke_fused_moe_wna16_cuda_kernel",
        "coords": [
            14,
            28,
            17
        ],
        "fiber": 28,
        "logic": "def invoke_fused_moe_wna16_cuda_kernel(A: torch.Tensor, B: torch.Tensor, C: torch.Tensor, B_scale: torch.Tensor | None, B_zp: torch.Tensor | None, topk_weights: torch.Tensor | None, sorted_token_ids: torch.Tensor | None, expert_ids: torch.Tensor, num_tokens_post_padded: torch.Tensor, mul_routed_weight: bool, top_k: int, config: dict[str, Any], block_shape: list[int]):\n    assert B_scale is not None and B_scale.ndim == 3\n    assert B_zp is None or B_zp.ndim == 3\n    assert block_shape is None or block_shape[0] == 0\n    M = A.size(0)\n    num_tokens = M * top_k\n    bit = 4\n    config = config.copy()\n    config.update(get_moe_wna16_block_config(config=config, use_moe_wna16_cuda=True, num_valid_tokens=num_tokens, size_k=A.size(1), size_n=B.size(1), num_experts=B.size(1), group_size=block_shape[1], real_top_k=top_k, block_size_m=config['BLOCK_SIZE_M']))\n    ops.moe_wna16_gemm(A, C, B, B_scale, B_zp, topk_weights if mul_routed_weight else None, sorted_token_ids, expert_ids, num_tokens_post_padded, top_k, config['BLOCK_SIZE_M'], config['BLOCK_SIZE_N'], config['BLOCK_SIZE_K'], bit)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "invoke_fused_moe_wna16_triton_kernel",
        "coords": [
            11,
            13,
            1
        ],
        "fiber": 25,
        "logic": "def invoke_fused_moe_wna16_triton_kernel(A: torch.Tensor, B: torch.Tensor, C: torch.Tensor, B_scale: torch.Tensor | None, B_zp: torch.Tensor | None, topk_weights: torch.Tensor | None, sorted_token_ids: torch.Tensor, expert_ids: torch.Tensor, num_tokens_post_padded: torch.Tensor, mul_routed_weight: bool, top_k: int, config: dict[str, Any], compute_type: tl.dtype, use_int8_w8a16: bool, use_int4_w4a16: bool, block_shape: list[int] | None):\n    assert B_scale is not None and B_scale.ndim == 3\n    assert B_zp is None or B_zp.ndim == 3\n    assert block_shape is not None and block_shape[0] == 0\n    M = A.size(0)\n    num_tokens = M * top_k\n    EM = sorted_token_ids.size(0)\n    if A.size(0) < config['BLOCK_SIZE_M']:\n        EM = min(sorted_token_ids.size(0), A.size(0) * top_k * config['BLOCK_SIZE_M'])\n    grid = lambda META: (triton.cdiv(EM, META['BLOCK_SIZE_M']) * triton.cdiv(B.size(1), META['BLOCK_SIZE_N']),)\n    config = config.copy()\n    config.update(get_moe_wna16_block_config(config=config, use_moe_wna16_cuda=False, num_valid_tokens=num_tokens, size_k=A.size(1), size_n=B.size(1), num_experts=B.size(1), group_size=block_shape[1], real_top_k=top_k, block_size_m=config['BLOCK_SIZE_M']))\n    fused_moe_kernel_gptq_awq[grid](A, B, C, B_scale, B_zp, topk_weights, sorted_token_ids, expert_ids, num_tokens_post_padded, B.size(1), A.size(1), EM, num_tokens, A.stride(0), A.stride(1), B.stride(0), B.stride(2), B.stride(1), C.stride(1), C.stride(2), B_scale.stride(0), B_scale.stride(2), B_scale.stride(1), B_zp.stride(0) if B_zp is not None else 0, B_zp.stride(2) if B_zp is not None else 0, B_zp.stride(1) if B_zp is not None else 0, block_k_diviable=A.size(1) % config['BLOCK_SIZE_K'] == 0, group_size=block_shape[1], MUL_ROUTED_WEIGHT=mul_routed_weight, top_k=top_k, compute_type=compute_type, has_zp=B_zp is not None, use_int4_w4a16=use_int4_w4a16, use_int8_w8a16=use_int8_w8a16, **config)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "invoke_fused_moe_triton_kernel",
        "coords": [
            24,
            18,
            28
        ],
        "fiber": 8,
        "logic": "def invoke_fused_moe_triton_kernel(A: torch.Tensor, B: torch.Tensor, C: torch.Tensor, A_scale: torch.Tensor | None, B_scale: torch.Tensor | None, topk_weights: torch.Tensor | None, sorted_token_ids: torch.Tensor | None, expert_ids: torch.Tensor, num_tokens_post_padded: torch.Tensor, mul_routed_weight: bool, top_k: int, config: dict[str, Any], compute_type: tl.dtype, use_fp8_w8a8: bool, use_int8_w8a8: bool, use_int8_w8a16: bool, use_int4_w4a16: bool, per_channel_quant: bool, block_shape: list[int] | None=None, B_bias: torch.Tensor | None=None):\n    assert topk_weights is not None or not mul_routed_weight\n    assert topk_weights is None or topk_weights.stride(1) == 1\n    assert sorted_token_ids is None or sorted_token_ids.stride(0) == 1\n    if use_fp8_w8a8 or use_int8_w8a8:\n        assert B_scale is not None\n        assert block_shape is None or triton.cdiv(B.size(-2), block_shape[0]) == B_scale.size(-2)\n        assert block_shape is None or triton.cdiv(B.size(-1), block_shape[1]) == B_scale.size(-1)\n    elif use_int8_w8a16 or use_int4_w4a16:\n        assert B_scale is not None\n        assert block_shape is None or block_shape[0] == 0\n    else:\n        assert A_scale is None\n        assert B_scale is None\n    M = A.size(0)\n    num_tokens = M * top_k\n    if sorted_token_ids is not None:\n        EM = sorted_token_ids.size(0)\n        if A.size(0) < config['BLOCK_SIZE_M']:\n            EM = min(sorted_token_ids.size(0), A.size(0) * top_k * config['BLOCK_SIZE_M'])\n    else:\n        EM = num_tokens * config['BLOCK_SIZE_M']\n    grid = lambda META: (triton.cdiv(EM, META['BLOCK_SIZE_M']) * triton.cdiv(B.size(1), META['BLOCK_SIZE_N']),)\n    HAS_BIAS = B_bias is not None\n    config = config.copy()\n    config['SPLIT_K'] = 1\n    BLOCK_SIZE_K = config.pop('BLOCK_SIZE_K')\n    if block_shape is not None:\n        BLOCK_SIZE_K = min(BLOCK_SIZE_K, min(block_shape[0], block_shape[1]))\n    fused_moe_kernel[grid](A, B, C, B_bias, A_scale, B_scale, topk_weights, sorted_token_ids, expert_ids, num_tokens_post_padded, B.size(1), B.size(2), EM, num_tokens, A.stride(0), A.stride(1), B.stride(0), B.stride(2), B.stride(1), C.stride(1), C.stride(2), A_scale.stride(0) if A_scale is not None and A_scale.ndim == 2 else 0, A_scale.stride(1) if A_scale is not None and A_scale.ndim == 2 else 0, B_scale.stride(0) if B_scale is not None and B_scale.ndim >= 2 else 0, B_scale.stride(2) if B_scale is not None and B_scale.ndim == 3 else 0, B_scale.stride(1) if B_scale is not None and B_scale.ndim >= 2 else 0, B_bias.stride(0) if B_bias is not None else 0, B_bias.stride(1) if B_bias is not None else 0, 0 if block_shape is None else block_shape[0], 0 if block_shape is None else block_shape[1], MUL_ROUTED_WEIGHT=mul_routed_weight, top_k=top_k, compute_type=compute_type, use_fp8_w8a8=use_fp8_w8a8, use_int8_w8a8=use_int8_w8a8, use_int8_w8a16=use_int8_w8a16, per_channel_quant=per_channel_quant, naive_block_assignment=sorted_token_ids is None, HAS_BIAS=HAS_BIAS, BLOCK_SIZE_K=BLOCK_SIZE_K, **config)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "dispatch_fused_moe_kernel",
        "coords": [
            6,
            22,
            6
        ],
        "fiber": 3,
        "logic": "def dispatch_fused_moe_kernel(A: torch.Tensor, B: torch.Tensor, C: torch.Tensor, A_scale: torch.Tensor | None, B_scale: torch.Tensor | None, B_zp: torch.Tensor | None, topk_weights: torch.Tensor | None, sorted_token_ids: torch.Tensor | None, expert_ids: torch.Tensor, num_tokens_post_padded: torch.Tensor, mul_routed_weight: bool, top_k: int, config: dict[str, Any], compute_type: tl.dtype, use_fp8_w8a8: bool, use_int8_w8a8: bool, use_int8_w8a16: bool, use_int4_w4a16: bool, per_channel_quant: bool, block_shape: list[int] | None=None, B_bias: torch.Tensor | None=None) -> None:\n    assert topk_weights is not None or not mul_routed_weight\n    assert topk_weights is None or topk_weights.stride(1) == 1\n    assert sorted_token_ids is None or sorted_token_ids.stride(0) == 1\n    M = A.size(0)\n    num_tokens = M * top_k\n    if (use_int8_w8a16 or use_int4_w4a16) and (block_shape is not None and block_shape[1] > 0):\n        assert B_bias is None\n        use_moe_wna16_cuda = should_moe_wna16_use_cuda(num_valid_tokens=num_tokens, group_size=block_shape[1], num_experts=B.size(0), bit=4 if use_int4_w4a16 else 8)\n        if use_moe_wna16_cuda:\n            invoke_fused_moe_wna16_cuda_kernel(A, B, C, B_scale, B_zp, topk_weights, sorted_token_ids, expert_ids, num_tokens_post_padded, mul_routed_weight, top_k, config, block_shape)\n            return\n        invoke_fused_moe_wna16_triton_kernel(A, B, C, B_scale, B_zp, topk_weights, sorted_token_ids, expert_ids, num_tokens_post_padded, mul_routed_weight, top_k, config, compute_type, use_int8_w8a16, use_int4_w4a16, block_shape)\n    else:\n        invoke_fused_moe_triton_kernel(A, B, C, A_scale, B_scale, topk_weights, sorted_token_ids, expert_ids, num_tokens_post_padded, mul_routed_weight, top_k, config, compute_type, use_fp8_w8a8, use_int8_w8a8, use_int8_w8a16, use_int4_w4a16, per_channel_quant, block_shape, B_bias)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "compute_identity_kernel",
        "coords": [
            23,
            21,
            18
        ],
        "fiber": 0,
        "logic": "@triton.jit\ndef compute_identity_kernel(top_k: int, hidden_states_ptr: tl.tensor, expert_scales_ptr: tl.tensor, num_tokens: int, output_ptr: tl.tensor, hidden_dim: int, scales_stride: int, BLOCK_SIZE: tl.constexpr) -> None:\n    pid = tl.program_id(0)\n    batch_id = pid // (hidden_dim // BLOCK_SIZE)\n    dim_offset = pid % (hidden_dim // BLOCK_SIZE) * BLOCK_SIZE\n    if batch_id >= num_tokens or dim_offset >= hidden_dim:\n        return\n    h = tl.load(hidden_states_ptr + batch_id * hidden_dim + dim_offset + tl.arange(0, BLOCK_SIZE), mask=dim_offset + tl.arange(0, BLOCK_SIZE) < hidden_dim)\n    result = tl.zeros([BLOCK_SIZE], dtype=tl.float32)\n    for i in range(top_k):\n        scale = tl.load(expert_scales_ptr + batch_id * scales_stride + i)\n        result += h * scale\n    tl.store(output_ptr + batch_id * hidden_dim + dim_offset + tl.arange(0, BLOCK_SIZE), result, mask=dim_offset + tl.arange(0, BLOCK_SIZE) < hidden_dim)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/fused_moe.py"
    },
    {
        "id": "_select_kernel_cls",
        "coords": [
            29,
            9,
            1
        ],
        "fiber": 8,
        "logic": "def _select_kernel_cls(backend: Fp8MoeBackend, config: FusedMoEConfig) -> type[mk.FusedMoEExperts]:\n    \"\"\"Select the first supported expert class for the MXFP8 config.\"\"\"\n    activation_format = mk.FusedMoEActivationFormat.BatchedExperts if config.moe_parallel_config.use_batched_activation_format else mk.FusedMoEActivationFormat.Standard\n    last_reason: str | None = None\n    for cls in backend_to_kernel_cls(backend):\n        supported, reason = cls.is_supported_config(cls, config, kMxfp8Static, kMxfp8Dynamic, activation_format)\n        if supported:\n            return cls\n        last_reason = reason\n    raise ValueError(f'No supported MXFP8 expert class for {backend.value}: {last_reason}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/mxfp8.py"
    },
    {
        "id": "backend_to_kernel_cls",
        "coords": [
            15,
            12,
            1
        ],
        "fiber": 28,
        "logic": "def backend_to_kernel_cls(backend: NvFp4MoeBackend) -> list[type[mk.FusedMoEExperts]]:\n    if backend == NvFp4MoeBackend.FLASHINFER_TRTLLM:\n        from vllm.model_executor.layers.fused_moe.experts.trtllm_nvfp4_moe import TrtLlmNvFp4ExpertsModular, TrtLlmNvFp4ExpertsMonolithic\n        return [TrtLlmNvFp4ExpertsMonolithic, TrtLlmNvFp4ExpertsModular]\n    elif backend == NvFp4MoeBackend.FLASHINFER_CUTLASS:\n        from vllm.model_executor.layers.fused_moe.flashinfer_cutlass_moe import FlashInferExperts\n        return [FlashInferExperts]\n    elif backend == NvFp4MoeBackend.FLASHINFER_CUTEDSL:\n        from vllm.model_executor.layers.fused_moe.experts.flashinfer_cutedsl_moe import FlashInferCuteDSLExperts\n        return [FlashInferCuteDSLExperts]\n    elif backend == NvFp4MoeBackend.VLLM_CUTLASS:\n        from vllm.model_executor.layers.fused_moe.cutlass_moe import CutlassExpertsFp4\n        return [CutlassExpertsFp4]\n    elif backend == NvFp4MoeBackend.MARLIN:\n        from vllm.model_executor.layers.fused_moe.fused_marlin_moe import MarlinExperts\n        return [MarlinExperts]\n    else:\n        raise ValueError(f'Unknown NvFP4 MoE backend: {backend.value}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/nvfp4.py"
    },
    {
        "id": "convert_to_nvfp4_moe_kernel_format",
        "coords": [
            8,
            29,
            5
        ],
        "fiber": 11,
        "logic": "def convert_to_nvfp4_moe_kernel_format(nvfp4_backend: NvFp4MoeBackend, layer: torch.nn.Module, w13: torch.Tensor, w13_scale: torch.Tensor, w13_scale_2: torch.Tensor, a13_scale: torch.Tensor | None, w2: torch.Tensor, w2_scale: torch.Tensor, w2_scale_2: torch.Tensor, a2_scale: torch.Tensor | None, is_act_and_mul: bool) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:\n    if nvfp4_backend in FLASHINFER_NVFP4_MOE_BACKENDS or nvfp4_backend == NvFp4MoeBackend.VLLM_CUTLASS:\n        w13, w13_scale, w13_scale_2, a13_scale, w2, w2_scale, w2_scale_2, a2_scale = prepare_nvfp4_moe_layer_for_fi_or_cutlass(backend=nvfp4_backend, layer=layer, w13=w13, w13_scale=w13_scale, w13_scale_2=w13_scale_2, a13_scale=a13_scale, w2=w2, w2_scale=w2_scale, w2_scale_2=w2_scale_2, a2_scale=a2_scale, is_act_and_mul=is_act_and_mul)\n    elif nvfp4_backend == NvFp4MoeBackend.MARLIN:\n        a13_scale = None\n        a2_scale = None\n        w13, w13_scale, w13_scale_2, w2, w2_scale, w2_scale_2 = prepare_nvfp4_moe_layer_for_marlin(layer=layer, w13=w13, w13_scale=w13_scale, w13_scale_2=w13_scale_2, w2=w2, w2_scale=w2_scale, w2_scale_2=w2_scale_2, is_act_and_mul=is_act_and_mul)\n    else:\n        raise ValueError(f'Unknown NvFp4 backend for MoE: {nvfp4_backend}')\n    return (w13, w13_scale, w13_scale_2, a13_scale, w2, w2_scale, w2_scale_2, a2_scale)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/nvfp4.py"
    },
    {
        "id": "make_nvfp4_moe_kernel",
        "coords": [
            6,
            29,
            27
        ],
        "fiber": 0,
        "logic": "def make_nvfp4_moe_kernel(moe_quant_config: FusedMoEQuantConfig, moe_config: FusedMoEConfig, experts_cls: type[mk.FusedMoEExperts], routing_tables: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None=None, shared_experts: SharedExperts | None=None) -> mk.FusedMoEKernel:\n    prepare_finalize = maybe_make_prepare_finalize(moe=moe_config, quant_config=moe_quant_config, routing_tables=routing_tables, allow_new_interface=True, use_monolithic=issubclass(experts_cls, mk.FusedMoEExpertsMonolithic))\n    assert prepare_finalize is not None\n    logger.info_once('Using %s', prepare_finalize.__class__.__name__)\n    if prepare_finalize.activation_format == mk.FusedMoEActivationFormat.BatchedExperts:\n        max_num_tokens = prepare_finalize.max_num_tokens_per_rank()\n        assert max_num_tokens is not None\n        experts = experts_cls(moe_config=moe_config, quant_config=moe_quant_config, max_num_tokens=max_num_tokens, num_dispatchers=prepare_finalize.num_dispatchers())\n    else:\n        experts = experts_cls(moe_config=moe_config, quant_config=moe_quant_config)\n    kernel = mk.FusedMoEKernel(prepare_finalize, experts, shared_experts=shared_experts, inplace=False)\n    return kernel",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/nvfp4.py"
    },
    {
        "id": "backend_to_kernel_cls",
        "coords": [
            15,
            12,
            1
        ],
        "fiber": 28,
        "logic": "def backend_to_kernel_cls(backend: Fp8MoeBackend) -> list[type[mk.FusedMoEExperts]]:\n    if backend == Fp8MoeBackend.FLASHINFER_TRTLLM:\n        from vllm.model_executor.layers.fused_moe.experts.trtllm_fp8_moe import TrtLlmFp8ExpertsModular, TrtLlmFp8ExpertsMonolithic\n        return [TrtLlmFp8ExpertsMonolithic, TrtLlmFp8ExpertsModular]\n    elif backend == Fp8MoeBackend.FLASHINFER_CUTLASS:\n        from vllm.model_executor.layers.fused_moe.flashinfer_cutlass_moe import FlashInferExperts\n        return [FlashInferExperts]\n    elif backend == Fp8MoeBackend.DEEPGEMM:\n        from vllm.model_executor.layers.fused_moe.triton_deep_gemm_moe import TritonOrDeepGemmExperts\n        return [TritonOrDeepGemmExperts]\n    elif backend == Fp8MoeBackend.BATCHED_DEEPGEMM:\n        from vllm.model_executor.layers.fused_moe.batched_deep_gemm_moe import BatchedDeepGemmExperts\n        return [BatchedDeepGemmExperts]\n    elif backend == Fp8MoeBackend.MARLIN:\n        from vllm.model_executor.layers.fused_moe.fused_marlin_moe import MarlinExperts\n        return [MarlinExperts]\n    elif backend == Fp8MoeBackend.TRITON:\n        from vllm.model_executor.layers.fused_moe.fused_moe import TritonExperts\n        return [TritonExperts]\n    elif backend == Fp8MoeBackend.BATCHED_TRITON:\n        from vllm.model_executor.layers.fused_moe.fused_batched_moe import BatchedTritonExperts\n        return [BatchedTritonExperts]\n    elif backend == Fp8MoeBackend.AITER:\n        from vllm.model_executor.layers.fused_moe.rocm_aiter_fused_moe import AiterExperts\n        return [AiterExperts]\n    elif backend == Fp8MoeBackend.VLLM_CUTLASS:\n        from vllm.model_executor.layers.fused_moe.triton_cutlass_moe import TritonOrCutlassExperts\n        return [TritonOrCutlassExperts]\n    elif backend == Fp8MoeBackend.BATCHED_VLLM_CUTLASS:\n        from vllm.model_executor.layers.fused_moe.cutlass_moe import CutlassBatchedExpertsFp8\n        return [CutlassBatchedExpertsFp8]\n    elif backend == Fp8MoeBackend.XPU:\n        from vllm.model_executor.layers.fused_moe.xpu_fused_moe import XPUExpertsFp8\n        return [XPUExpertsFp8]\n    else:\n        raise ValueError(f'Unknown FP8 MoE backend: {backend.value}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/fp8.py"
    },
    {
        "id": "convert_to_fp8_moe_kernel_format",
        "coords": [
            24,
            8,
            7
        ],
        "fiber": 8,
        "logic": "def convert_to_fp8_moe_kernel_format(fp8_backend: Fp8MoeBackend, layer: torch.nn.Module, w13: torch.Tensor, w2: torch.Tensor, w13_scale: torch.Tensor, w2_scale: torch.Tensor, w13_input_scale: torch.Tensor | None, w2_input_scale: torch.Tensor | None) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:\n    block_quant = hasattr(layer, 'weight_block_size')\n    if fp8_backend in [Fp8MoeBackend.DEEPGEMM, Fp8MoeBackend.BATCHED_DEEPGEMM]:\n        assert block_quant\n        w13, w2, w13_scale, w2_scale = prepare_fp8_moe_layer_for_deepgemm(w13, w2, w13_scale, w2_scale, tuple(layer.weight_block_size))\n    elif fp8_backend == Fp8MoeBackend.AITER:\n        w13, w2 = rocm_aiter_ops.shuffle_weights(w13, w2)\n    elif fp8_backend == Fp8MoeBackend.MARLIN:\n        weight_block_size = getattr(layer, 'weight_block_size', None)\n        if weight_block_size == [1, 32]:\n            from vllm.model_executor.layers.quantization.utils.marlin_utils_fp8 import prepare_mxfp8_moe_layer_for_marlin\n            w13, w2, w13_scale, w2_scale = prepare_mxfp8_moe_layer_for_marlin(layer, w13, w2, w13_scale, w2_scale)\n        else:\n            w13, w2, w13_scale, w2_scale = prepare_fp8_moe_layer_for_marlin(layer, w13, w2, w13_scale, w2_scale)\n    elif fp8_backend in [Fp8MoeBackend.FLASHINFER_CUTLASS, Fp8MoeBackend.FLASHINFER_TRTLLM]:\n        w13, w2, w13_scale, w2_scale = prepare_fp8_moe_layer_for_fi(layer=layer, w13=w13, w2=w2, w13_scale=w13_scale, w13_input_scale=w13_input_scale, w2_scale=w2_scale, w2_input_scale=w2_input_scale, is_trtllm=fp8_backend == Fp8MoeBackend.FLASHINFER_TRTLLM)\n    elif fp8_backend not in [Fp8MoeBackend.TRITON, Fp8MoeBackend.BATCHED_TRITON, Fp8MoeBackend.VLLM_CUTLASS, Fp8MoeBackend.BATCHED_VLLM_CUTLASS, Fp8MoeBackend.XPU]:\n        raise ValueError(f'Unsupported FP8 MoE backend: {fp8_backend.value}')\n    return (w13, w2, w13_scale, w2_scale)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/fp8.py"
    },
    {
        "id": "make_fp8_moe_kernel",
        "coords": [
            14,
            11,
            21
        ],
        "fiber": 15,
        "logic": "def make_fp8_moe_kernel(moe_quant_config: FusedMoEQuantConfig, moe_config: FusedMoEConfig, experts_cls: type[mk.FusedMoEExperts], fp8_backend: Fp8MoeBackend, routing_tables: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None=None, shared_experts: SharedExperts | None=None) -> mk.FusedMoEKernel:\n    prepare_finalize = maybe_make_prepare_finalize(moe=moe_config, quant_config=moe_quant_config, routing_tables=routing_tables, allow_new_interface=True, use_monolithic=issubclass(experts_cls, mk.FusedMoEExpertsMonolithic))\n    assert prepare_finalize is not None\n    logger.info_once('Using %s', prepare_finalize.__class__.__name__, scope='local')\n    if prepare_finalize.activation_format == mk.FusedMoEActivationFormat.BatchedExperts:\n        max_num_tokens = prepare_finalize.max_num_tokens_per_rank()\n        assert max_num_tokens is not None\n        experts = experts_cls(moe_config=moe_config, quant_config=moe_quant_config, max_num_tokens=max_num_tokens, num_dispatchers=prepare_finalize.num_dispatchers())\n    else:\n        experts = experts_cls(moe_config=moe_config, quant_config=moe_quant_config)\n    kernel = mk.FusedMoEKernel(prepare_finalize, experts, shared_experts=shared_experts, inplace=not moe_config.disable_inplace and fp8_backend != Fp8MoeBackend.FLASHINFER_CUTLASS)\n    return kernel",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/fp8.py"
    },
    {
        "id": "backend_to_kernel_cls",
        "coords": [
            15,
            12,
            1
        ],
        "fiber": 28,
        "logic": "def backend_to_kernel_cls(backend: UnquantizedMoeBackend) -> type[mk.FusedMoEExperts]:\n    if backend == UnquantizedMoeBackend.FLASHINFER_TRTLLM:\n        from vllm.model_executor.layers.fused_moe.experts.trtllm_bf16_moe import TrtLlmBf16Experts\n        return TrtLlmBf16Experts\n    elif backend == UnquantizedMoeBackend.FLASHINFER_CUTLASS:\n        from vllm.model_executor.layers.fused_moe.flashinfer_cutlass_moe import FlashInferExperts\n        return FlashInferExperts\n    elif backend == UnquantizedMoeBackend.AITER:\n        from vllm.model_executor.layers.fused_moe.rocm_aiter_fused_moe import AiterExperts\n        return AiterExperts\n    elif backend == UnquantizedMoeBackend.TRITON:\n        from vllm.model_executor.layers.fused_moe.fused_moe import TritonExperts\n        return TritonExperts\n    elif backend == UnquantizedMoeBackend.BATCHED_TRITON:\n        from vllm.model_executor.layers.fused_moe.fused_batched_moe import BatchedTritonExperts\n        return BatchedTritonExperts\n    elif backend == UnquantizedMoeBackend.XPU:\n        from vllm.model_executor.layers.fused_moe.xpu_fused_moe import XPUExperts\n        return XPUExperts\n    else:\n        raise ValueError(f'Unknown unquantized MoE backend: {backend.value}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/unquantized.py"
    },
    {
        "id": "convert_to_unquantized_kernel_format",
        "coords": [
            30,
            24,
            16
        ],
        "fiber": 8,
        "logic": "def convert_to_unquantized_kernel_format(unquantized_backend: UnquantizedMoeBackend, layer: Module, w13_weight: torch.Tensor, w2_weight: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:\n    if unquantized_backend == UnquantizedMoeBackend.AITER:\n        w13_weight, w2_weight = rocm_aiter_ops.shuffle_weights(w13_weight, w2_weight)\n    elif unquantized_backend == UnquantizedMoeBackend.FLASHINFER_CUTLASS:\n        if layer.moe_config.is_act_and_mul:\n            w13_weight = swap_w13_to_w31(w13_weight)\n    elif unquantized_backend == UnquantizedMoeBackend.FLASHINFER_TRTLLM:\n        w13_weight = swap_w13_to_w31(w13_weight)\n        _cache_permute_indices: dict[torch.Size, torch.Tensor] = {}\n        w13_weight, w2_weight = convert_moe_weights_to_flashinfer_trtllm_block_layout(_cache_permute_indices, w13_weight, w2_weight)\n    return (w13_weight.contiguous(), w2_weight.contiguous())",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/unquantized.py"
    },
    {
        "id": "make_unquantized_moe_kernel",
        "coords": [
            11,
            4,
            11
        ],
        "fiber": 26,
        "logic": "def make_unquantized_moe_kernel(quant_config: FusedMoEQuantConfig, moe_config: FusedMoEConfig, backend: UnquantizedMoeBackend, experts_cls: type[mk.FusedMoEExperts], routing_tables: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None=None, shared_experts: SharedExperts | None=None) -> mk.FusedMoEKernel:\n    is_monolithic = issubclass(experts_cls, mk.FusedMoEExpertsMonolithic)\n    prepare_finalize = maybe_make_prepare_finalize(moe=moe_config, quant_config=quant_config, routing_tables=routing_tables, allow_new_interface=True, use_monolithic=is_monolithic)\n    assert prepare_finalize is not None\n    logger.info_once('Using %s', prepare_finalize.__class__.__name__, scope='local')\n    if prepare_finalize.activation_format == mk.FusedMoEActivationFormat.BatchedExperts:\n        max_num_tokens = prepare_finalize.max_num_tokens_per_rank()\n        assert max_num_tokens is not None\n        experts = experts_cls(moe_config=moe_config, quant_config=quant_config, max_num_tokens=max_num_tokens, num_dispatchers=prepare_finalize.num_dispatchers())\n    else:\n        experts = experts_cls(moe_config=moe_config, quant_config=quant_config)\n    kernel = mk.FusedMoEKernel(prepare_finalize, experts, shared_experts=shared_experts, inplace=not moe_config.disable_inplace and (not is_monolithic))\n    return kernel",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/unquantized.py"
    },
    {
        "id": "backend_to_kernel_cls",
        "coords": [
            15,
            12,
            1
        ],
        "fiber": 28,
        "logic": "def backend_to_kernel_cls(backend: Mxfp4MoeBackend) -> list[type[mk.FusedMoEExperts]]:\n    if backend in (Mxfp4MoeBackend.FLASHINFER_TRTLLM_MXFP4_BF16, Mxfp4MoeBackend.FLASHINFER_TRTLLM_MXFP4_MXFP8):\n        from vllm.model_executor.layers.fused_moe.experts.trtllm_mxfp4_moe import TrtLlmMxfp4ExpertsModular, TrtLlmMxfp4ExpertsMonolithic\n        return [TrtLlmMxfp4ExpertsMonolithic, TrtLlmMxfp4ExpertsModular]\n    elif backend in (Mxfp4MoeBackend.FLASHINFER_CUTLASS_MXFP4_BF16, Mxfp4MoeBackend.FLASHINFER_CUTLASS_MXFP4_MXFP8):\n        from vllm.model_executor.layers.fused_moe.flashinfer_cutlass_moe import FlashInferExperts\n        return [FlashInferExperts]\n    elif backend == Mxfp4MoeBackend.TRITON:\n        from vllm.model_executor.layers.fused_moe.gpt_oss_triton_kernels_moe import OAITritonExperts, OAITritonMxfp4ExpertsMonolithic\n        return [OAITritonMxfp4ExpertsMonolithic, OAITritonExperts]\n    elif backend == Mxfp4MoeBackend.TRITON_UNFUSED:\n        from vllm.model_executor.layers.fused_moe.gpt_oss_triton_kernels_moe import UnfusedOAITritonExperts\n        return [UnfusedOAITritonExperts]\n    elif backend == Mxfp4MoeBackend.MARLIN:\n        from vllm.model_executor.layers.fused_moe.fused_marlin_moe import MarlinExperts\n        return [MarlinExperts]\n    elif backend == Mxfp4MoeBackend.BATCHED_MARLIN:\n        from vllm.model_executor.layers.fused_moe.fused_marlin_moe import BatchedMarlinExperts\n        return [BatchedMarlinExperts]\n    elif backend == Mxfp4MoeBackend.AITER:\n        from vllm.model_executor.layers.fused_moe.rocm_aiter_fused_moe import AiterExperts\n        return [AiterExperts]\n    elif backend == Mxfp4MoeBackend.XPU:\n        from vllm.model_executor.layers.fused_moe.xpu_fused_moe import XPUExpertsMXFp4\n        return [XPUExpertsMXFp4]\n    else:\n        raise ValueError(f'Unknown MXFP4 MoE backend: {backend.value}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/mxfp4.py"
    },
    {
        "id": "convert_to_mxfp4_moe_kernel_format",
        "coords": [
            17,
            29,
            20
        ],
        "fiber": 4,
        "logic": "def convert_to_mxfp4_moe_kernel_format(mxfp4_backend: Mxfp4MoeBackend, layer: torch.nn.Module, w13_weight: torch.Tensor, w2_weight: torch.Tensor, w13_weight_scale: torch.Tensor, w2_weight_scale: torch.Tensor, w13_bias: torch.Tensor | None=None, w2_bias: torch.Tensor | None=None, _cache_permute_indices: dict[torch.Size, torch.Tensor] | None=None) -> tuple[torch.Tensor, torch.Tensor, Union[torch.Tensor, 'PrecisionConfig'], Union[torch.Tensor, 'PrecisionConfig'], torch.Tensor | None, torch.Tensor | None]:\n    \"\"\"Convert loaded weights into backend-specific kernel format.\"\"\"\n    num_experts = w13_weight.shape[0]\n    intermediate_size = w13_weight.shape[1] // 2\n    hidden_size = w13_weight.shape[2] * 2\n    sf_block_size = 32\n    if mxfp4_backend in (Mxfp4MoeBackend.MARLIN, Mxfp4MoeBackend.BATCHED_MARLIN):\n        from vllm.model_executor.layers.quantization.utils.marlin_utils_fp4 import prepare_moe_mxfp4_layer_for_marlin\n        return prepare_moe_mxfp4_layer_for_marlin(layer, w13_weight, w2_weight, w13_weight_scale, w2_weight_scale, w13_bias, w2_bias)\n    elif mxfp4_backend in TRTLLM_BACKENDS:\n        assert _cache_permute_indices is not None\n        from flashinfer.fp4_quantization import nvfp4_block_scale_interleave\n        from flashinfer.fused_moe.core import get_w2_permute_indices_with_cache\n        w13_weight = w13_weight.data\n        w2_weight = w2_weight.data\n        w13_weight_scale = w13_weight_scale.data\n        w2_weight_scale = w2_weight_scale.data\n        assert w13_bias is not None and w2_bias is not None\n        w13_bias = w13_bias.data.to(torch.float32)\n        w2_bias = w2_bias.data.to(torch.float32)\n\n        def swap_every_two_rows(x, axis=-1):\n            shape = x.shape\n            if axis < 0:\n                axis = len(shape) + axis\n            new_shape = list(shape)\n            new_shape[axis] = shape[axis] // 2\n            new_shape.insert(axis + 1, 2)\n            x = x.reshape(*new_shape)\n            x = x.flip(axis + 1)\n            new_shape = list(shape)\n            return x.reshape(*new_shape)\n        w13_weight_scale = swap_every_two_rows(w13_weight_scale, -2)\n        w13_weight = swap_every_two_rows(w13_weight, -2)\n        w13_bias = swap_every_two_rows(w13_bias, -1)\n        gemm1_weights_shuffled = []\n        gemm1_scales_shuffled = []\n        gemm2_weights_shuffled = []\n        gemm2_scales_shuffled = []\n        gemm1_bias_shuffled = []\n        gemm2_bias_shuffled = []\n        epilogue_tile_m = 128\n        for i in range(num_experts):\n            permute_indices = get_w2_permute_indices_with_cache(_cache_permute_indices, w13_weight[i].view(torch.uint8), epilogue_tile_m)\n            gemm1_weights_shuffled.append(w13_weight[i].view(torch.uint8)[permute_indices.to(w13_weight.device)].contiguous())\n            permute_sf_indices = get_w2_permute_indices_with_cache(_cache_permute_indices, w13_weight_scale[i].view(torch.uint8), epilogue_tile_m, num_elts_per_sf=16)\n            gemm1_scales_shuffled.append(nvfp4_block_scale_interleave(w13_weight_scale[i].view(torch.uint8)[permute_sf_indices.to(w13_weight_scale.device)].contiguous()))\n            permute_bias_indices = get_w2_permute_indices_with_cache(_cache_permute_indices, w13_bias[i].clone().reshape(-1, 1), epilogue_tile_m)\n            gemm1_bias_shuffled.append(w13_bias[i].clone().reshape(-1, 1)[permute_bias_indices.to(w13_bias.device)].contiguous())\n            permute_indices = get_w2_permute_indices_with_cache(_cache_permute_indices, w2_weight[i].view(torch.uint8), epilogue_tile_m)\n            gemm2_weights_shuffled.append(w2_weight[i].view(torch.uint8)[permute_indices.to(w2_weight.device)].contiguous())\n            permute_sf_indices = get_w2_permute_indices_with_cache(_cache_permute_indices, w2_weight_scale[i].view(torch.uint8), epilogue_tile_m, num_elts_per_sf=16)\n            gemm2_scales_shuffled.append(nvfp4_block_scale_interleave(w2_weight_scale[i].view(torch.uint8)[permute_sf_indices.to(w2_weight_scale.device)].contiguous()))\n            permute_indices = get_w2_permute_indices_with_cache(_cache_permute_indices, w2_bias[i].clone().reshape(-1, 1), epilogue_tile_m)\n            gemm2_bias_shuffled.append(w2_bias[i].clone().reshape(-1, 1)[permute_indices.to(w2_bias.device)].contiguous())\n        w13_weight = torch.stack(gemm1_weights_shuffled)\n        w13_weight_scale = torch.stack(gemm1_scales_shuffled).reshape(num_experts, 2 * intermediate_size, hidden_size // sf_block_size).view(torch.float8_e4m3fn)\n        w2_weight = torch.stack(gemm2_weights_shuffled)\n        w2_weight_scale = torch.stack(gemm2_scales_shuffled).reshape(num_experts, hidden_size, intermediate_size // sf_block_size).view(torch.float8_e4m3fn)\n        w13_bias = torch.stack(gemm1_bias_shuffled).reshape(num_experts, -1)\n        w2_bias = torch.stack(gemm2_bias_shuffled).reshape(num_experts, -1)\n        return (w13_weight, w2_weight, w13_weight_scale, w2_weight_scale, w13_bias, w2_bias)\n    elif mxfp4_backend in (Mxfp4MoeBackend.FLASHINFER_CUTLASS_MXFP4_BF16, Mxfp4MoeBackend.FLASHINFER_CUTLASS_MXFP4_MXFP8):\n        w13_w = w13_weight.data\n        gate_w, up_w = (w13_w[:, ::2, :], w13_w[:, 1::2, :])\n        deinterleaved_w13_w = torch.cat([gate_w, up_w], dim=1)\n        w1_w, w3_w = torch.chunk(deinterleaved_w13_w, 2, dim=1)\n        w13_weight_swapped = torch.cat([w3_w, w1_w], dim=1)\n        assert w13_bias is not None and w2_bias is not None\n        w13_b = w13_bias.data.to(torch.float32)\n        gate_b, up_b = (w13_b[:, ::2], w13_b[:, 1::2])\n        deinterleaved_w13_b = torch.cat([gate_b, up_b], dim=1)\n        b1, b3 = torch.chunk(deinterleaved_w13_b, 2, dim=-1)\n        w13_bias_swapped = torch.cat([b3, b1], dim=-1).to(torch.bfloat16)\n        w13_s = w13_weight_scale.data\n        gate_s, up_s = (w13_s[:, ::2, :], w13_s[:, 1::2, :])\n        deinterleaved_w13_s = torch.cat([gate_s, up_s], dim=1)\n        s1, s3 = torch.chunk(deinterleaved_w13_s, 2, dim=1)\n        w13_scale_swapped = torch.cat([s3, s1], dim=1)\n        if mxfp4_backend == Mxfp4MoeBackend.FLASHINFER_CUTLASS_MXFP4_MXFP8:\n            from flashinfer import block_scale_interleave\n            orig_shape = w13_scale_swapped.shape\n            w13_scale_interleaved = block_scale_interleave(w13_scale_swapped.view(torch.uint8)).reshape(orig_shape)\n            w2_s = w2_weight_scale.data\n            orig_shape = w2_s.shape\n            w2_scale_interleaved = block_scale_interleave(w2_s.view(torch.uint8)).reshape(orig_shape)\n            return (w13_weight_swapped, w2_weight, w13_scale_interleaved, w2_scale_interleaved, w13_bias_swapped, w2_bias)\n        else:\n            assert mxfp4_backend == Mxfp4MoeBackend.FLASHINFER_CUTLASS_MXFP4_BF16\n\n            def _interleave_mxfp4_cutlass_sm90(w):\n                w_shape = w.shape\n                w_interleaved = w.reshape(w_shape[0], w_shape[1], w_shape[2] // 4, 4)\n                w_interleaved = w_interleaved.permute(0, 2, 1, 3)\n                w_interleaved = w_interleaved.reshape(w_shape[0], w_shape[2] // 4, w_shape[1] * 4)\n                return w_interleaved\n            w31_scales = w13_scale_swapped.to(torch.uint8)\n            w31_scales_interleaved = _interleave_mxfp4_cutlass_sm90(w31_scales)\n            w2_scale = w2_weight_scale.data.to(torch.uint8)\n            w2_scale_interleaved = _interleave_mxfp4_cutlass_sm90(w2_scale)\n            return (w13_weight_swapped, w2_weight, w31_scales_interleaved, w2_scale_interleaved, w13_bias_swapped, w2_bias)\n    elif mxfp4_backend == Mxfp4MoeBackend.AITER:\n        from vllm._aiter_ops import rocm_aiter_ops\n        if w13_bias is not None:\n            w13_bias = w13_bias.data.to(torch.float32)\n        if w2_bias is not None:\n            w2_bias = w2_bias.data.to(torch.float32)\n        e, n, k = w13_weight.shape\n        w13_weight.view(torch.uint8).copy_(w13_weight.data.view(torch.uint8).view(e, n // 2, 2, k).permute(0, 2, 1, 3).contiguous().view(e, n, k))\n        w13_weight_scale.data = w13_weight_scale.data.view(e, n // 2, 2, -1).permute(0, 2, 1, 3).contiguous().view(e, n, -1)\n        w13_weight.data = w13_weight.data.view(torch.float4_e2m1fn_x2)\n        w2_weight.data = w2_weight.data.view(torch.float4_e2m1fn_x2)\n        w13_weight.data = rocm_aiter_ops.shuffle_weight_a16w4(w13_weight, 16, True)\n        shuffled_w13_scale = rocm_aiter_ops.shuffle_scale_a16w4(w13_weight_scale.view(-1, w13_weight_scale.shape[-1]), num_experts, True)\n        w2_weight.data = rocm_aiter_ops.shuffle_weight_a16w4(w2_weight, 16, False)\n        shuffled_w2_scale = rocm_aiter_ops.shuffle_scale_a16w4(w2_weight_scale.view(-1, w2_weight_scale.shape[-1]), num_experts, False)\n        if w13_bias is not None:\n            w13_bias = w13_bias.data.view(-1, n // 2, 2).permute(0, 2, 1).contiguous().view(-1, n)\n        return (w13_weight, w2_weight, shuffled_w13_scale, shuffled_w2_scale, w13_bias, w2_bias)\n    elif mxfp4_backend in TRITON_BACKENDS:\n        from triton_kernels.matmul_ogs import FlexCtx, PrecisionConfig\n        assert w13_bias is not None and w2_bias is not None\n        w13_bias = w13_bias.to(torch.float32)\n        w2_bias = w2_bias.to(torch.float32)\n        w13_weight, w13_flex, w13_scale = _swizzle_mxfp4(w13_weight, w13_weight_scale)\n        w2_weight, w2_flex, w2_scale = _swizzle_mxfp4(w2_weight, w2_weight_scale)\n        w13_precision_config = PrecisionConfig(weight_scale=w13_scale, flex_ctx=FlexCtx(rhs_data=w13_flex))\n        w2_precision_config = PrecisionConfig(weight_scale=w2_scale, flex_ctx=FlexCtx(rhs_data=w2_flex))\n        del layer.w13_weight\n        del layer.w2_weight\n        return (w13_weight, w2_weight, w13_precision_config, w2_precision_config, w13_bias, w2_bias)\n    elif mxfp4_backend == Mxfp4MoeBackend.XPU:\n        return (w13_weight, w2_weight, w13_weight_scale, w2_weight_scale, w13_bias, w2_bias)\n    else:\n        raise ValueError(f'Unsupported mxfp4_backend: {mxfp4_backend}: should be one of: {list(Mxfp4MoeBackend)}.')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/mxfp4.py"
    },
    {
        "id": "make_mxfp4_moe_kernel",
        "coords": [
            11,
            6,
            20
        ],
        "fiber": 6,
        "logic": "def make_mxfp4_moe_kernel(moe_quant_config: FusedMoEQuantConfig, moe_config: FusedMoEConfig, experts_cls: type[mk.FusedMoEExperts], mxfp4_backend: Mxfp4MoeBackend, routing_tables: tuple[torch.Tensor, torch.Tensor, torch.Tensor] | None=None, shared_experts: torch.nn.Module | None=None) -> mk.FusedMoEKernel:\n    \"\"\"Create a FusedMoEKernel for the given MXFP4 backend.\"\"\"\n    is_monolithic = issubclass(experts_cls, mk.FusedMoEExpertsMonolithic)\n    prepare_finalize = maybe_make_prepare_finalize(moe=moe_config, quant_config=moe_quant_config, routing_tables=routing_tables, allow_new_interface=True, use_monolithic=is_monolithic)\n    assert prepare_finalize is not None\n    logger.info_once('Using %s', prepare_finalize.__class__.__name__, scope='local')\n    if prepare_finalize.activation_format == mk.FusedMoEActivationFormat.BatchedExperts:\n        max_num_tokens = prepare_finalize.max_num_tokens_per_rank()\n        assert max_num_tokens is not None\n        experts = experts_cls(moe_config=moe_config, quant_config=moe_quant_config, max_num_tokens=max_num_tokens, num_dispatchers=prepare_finalize.num_dispatchers())\n    else:\n        experts = experts_cls(moe_config=moe_config, quant_config=moe_quant_config)\n    kernel = mk.FusedMoEKernel(prepare_finalize, experts, shared_experts=shared_experts if moe_config.moe_parallel_config.use_deepep_ll_kernels else None, inplace=not moe_config.disable_inplace and mxfp4_backend not in TRTLLM_BACKENDS)\n    return kernel",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/oracle/mxfp4.py"
    },
    {
        "id": "maybe_all_reduce_tensor_model_parallel",
        "coords": [
            22,
            21,
            15
        ],
        "fiber": 27,
        "logic": "def maybe_all_reduce_tensor_model_parallel(self, final_hidden_states: torch.Tensor):\n    \"\"\"\n        Some combine kernels reduce across GPU ranks by default.\n        \"\"\"\n    if self.must_reduce_shared_expert_outputs():\n        return final_hidden_states\n    else:\n        return tensor_model_parallel_all_reduce(final_hidden_states)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/runner/default_moe_runner.py"
    },
    {
        "id": "maybe_all_reduce_tensor_model_parallel",
        "coords": [
            22,
            21,
            15
        ],
        "fiber": 27,
        "logic": "@abstractmethod\ndef maybe_all_reduce_tensor_model_parallel(self, final_hidden_states: torch.Tensor):\n    raise NotImplementedError",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/runner/moe_runner.py"
    },
    {
        "id": "_eplb_map_and_record_i32_kernel",
        "coords": [
            10,
            28,
            3
        ],
        "fiber": 10,
        "logic": "@triton.jit\ndef _eplb_map_and_record_i32_kernel(topk_ids_ptr, logical_replica_count_ptr, logical_to_physical_ptr, out_ids_ptr, out_ptr, record_enabled_ptr, num_logical_experts, map_slots, out_size, numel, BLOCK_SIZE: tl.constexpr):\n    pid = tl.program_id(0)\n    offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)\n    mask = offs < numel\n    expert_id = tl.load(topk_ids_ptr + offs, mask=mask, other=0).to(tl.int64)\n    valid_expert = (expert_id >= 0) & (expert_id < num_logical_experts)\n    safe_expert_id = tl.where(valid_expert, expert_id, 0)\n    replica_count = tl.load(logical_replica_count_ptr + safe_expert_id, mask=mask & valid_expert, other=1)\n    replica_count = tl.maximum(replica_count, 1)\n    replica_idx = offs % replica_count\n    map_index = safe_expert_id * map_slots + replica_idx\n    physical_id = tl.load(logical_to_physical_ptr + map_index, mask=mask & valid_expert, other=-1)\n    tl.store(out_ids_ptr + offs, physical_id, mask=mask)\n    record_enabled = tl.load(record_enabled_ptr) != 0\n    valid = mask & record_enabled & (physical_id >= 0) & (physical_id < out_size)\n    safe_physical_id = tl.where(physical_id >= 0, physical_id, 0)\n    tl.atomic_add(out_ptr + safe_physical_id, 1, mask=valid)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/router/base_router.py"
    },
    {
        "id": "_validate_distribution_params",
        "coords": [
            23,
            12,
            16
        ],
        "fiber": 20,
        "logic": "def _validate_distribution_params(self):\n    \"\"\"Validate distribution type and parameters.\"\"\"\n    valid_distributions = ['uniform', 'normal']\n    if self.distribution not in valid_distributions:\n        raise ValueError(f'Unsupported distribution: {self.distribution}. Supported distributions: {valid_distributions}')\n    if self.distribution == 'normal':\n        self.distribution_params.setdefault('mean', 0.0)\n        self.distribution_params.setdefault('std', 1.0)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/router/routing_simulator_router.py"
    },
    {
        "id": "_sample_continuous_distribution",
        "coords": [
            24,
            10,
            7
        ],
        "fiber": 10,
        "logic": "def _sample_continuous_distribution(self, num_tokens: int, top_k: int, device: torch.device) -> torch.Tensor:\n    \"\"\"Sample from continuous distributions.\"\"\"\n    shape = (num_tokens, top_k)\n    if self.distribution == 'normal':\n        mean = self.distribution_params['mean']\n        std = self.distribution_params['std']\n        return torch.normal(mean, std, size=shape, device=device)\n    else:\n        raise ValueError(f'Unsupported continuous distribution: {self.distribution}')",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/router/routing_simulator_router.py"
    },
    {
        "id": "get_distribution_info",
        "coords": [
            20,
            5,
            14
        ],
        "fiber": 8,
        "logic": "def get_distribution_info(self) -> dict:\n    \"\"\"Get information about the current distribution configuration.\"\"\"\n    return {'distribution': self.distribution, 'parameters': self.distribution_params.copy()}",
        "origin": "/tmp/vllm_repo/vllm/model_executor/layers/fused_moe/router/routing_simulator_router.py"
    },
    {
        "id": "get_sparse_attention_config",
        "coords": [
            25,
            26,
            5
        ],
        "fiber": 25,
        "logic": "def get_sparse_attention_config(model_config: ModelConfig, load_config: LoadConfig, sparse_attention_config_filename: str='sparse_attention_config.json') -> dict[str, Any]:\n    model_name_or_path = model_config.model\n    is_local = os.path.isdir(model_name_or_path)\n    if not is_local:\n        with get_lock(model_name_or_path, load_config.download_dir):\n            hf_folder = snapshot_download(model_name_or_path, revision=model_config.revision, allow_patterns='*.json', cache_dir=load_config.download_dir, local_files_only=huggingface_hub.constants.HF_HUB_OFFLINE, tqdm_class=DisabledTqdm)\n    else:\n        hf_folder = model_name_or_path\n    config_file = os.path.join(hf_folder, sparse_attention_config_filename)\n    if not os.path.exists(config_file):\n        return {}\n    with open(config_file) as f:\n        config = json.load(f)\n    logger.info('Loaded sparse attention config from %s', config_file)\n    return config",
        "origin": "/tmp/vllm_repo/vllm/model_executor/model_loader/weight_utils.py"
    },
    {
        "id": "_place_kernel_tensors",
        "coords": [
            9,
            20,
            3
        ],
        "fiber": 1,
        "logic": "def _place_kernel_tensors(layer: torch.nn.Module, info: LayerReloadingInfo):\n    for name in get_layer_tensors(layer):\n        delattr(layer, name)\n    assert info.kernel_tensors is not None\n    parameters, buffers = info.kernel_tensors\n    for name, param in parameters.items():\n        layer.register_parameter(name, param)\n    for name, buffer in buffers.items():\n        layer.register_buffer(name, buffer)",
        "origin": "/tmp/vllm_repo/vllm/model_executor/model_loader/reload/layerwise.py"
    },
    {
        "id": "tensor_model_parallel_all_reduce",
        "coords": [
            30,
            26,
            30
        ],
        "fiber": 24,
        "logic": "def tensor_model_parallel_all_reduce(input_: torch.Tensor) -> torch.Tensor:\n    \"\"\"All-reduce the input tensor across model parallel group.\"\"\"\n    return get_tp_group().all_reduce(input_)",
        "origin": "/tmp/vllm_repo/vllm/distributed/communication_op.py"
    },
    {
        "id": "broadcast_tensor_dict",
        "coords": [
            18,
            13,
            5
        ],
        "fiber": 5,
        "logic": "def broadcast_tensor_dict(tensor_dict: dict[Any, torch.Tensor | Any] | None=None, src: int=0):\n    if not torch.distributed.is_initialized():\n        return tensor_dict\n    return get_tp_group().broadcast_tensor_dict(tensor_dict, src)",
        "origin": "/tmp/vllm_repo/vllm/distributed/communication_op.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, input_: torch.Tensor, src: int=0):\n    if self.world_size == 1:\n        return input_\n    if self.device_communicator and input_.is_cuda:\n        return self.device_communicator.broadcast(input_, src)\n    else:\n        return self.tcp_store_group.broadcast(input_, src)",
        "origin": "/tmp/vllm_repo/vllm/distributed/stateless_coordinator.py"
    },
    {
        "id": "broadcast_object",
        "coords": [
            25,
            30,
            29
        ],
        "fiber": 22,
        "logic": "def broadcast_object(self, obj=None, src: int=0):\n    if self.world_size == 1:\n        return obj\n    return self.tcp_store_group.broadcast_obj(obj, src)",
        "origin": "/tmp/vllm_repo/vllm/distributed/stateless_coordinator.py"
    },
    {
        "id": "broadcast_object_list",
        "coords": [
            12,
            26,
            30
        ],
        "fiber": 6,
        "logic": "def broadcast_object_list(self, obj_list: list[Any], src: int=0, group: ProcessGroup | None=None):\n    assert src < self.world_size\n    if self.world_size == 1:\n        return obj_list\n    if self.rank_in_group == src:\n        for obj in obj_list:\n            self.tcp_store_group.broadcast_obj(obj, src)\n    else:\n        for i in range(len(obj_list)):\n            obj_list[i] = self.tcp_store_group.broadcast_obj(None, src)\n    return obj_list",
        "origin": "/tmp/vllm_repo/vllm/distributed/stateless_coordinator.py"
    },
    {
        "id": "broadcast_tensor_dict",
        "coords": [
            18,
            13,
            5
        ],
        "fiber": 5,
        "logic": "def broadcast_tensor_dict(self, tensor_dict: dict[str, torch.Tensor | Any] | None=None, src: int=0, group: ProcessGroup | None=None, metadata_group: ProcessGroup | None=None) -> dict[str, torch.Tensor | Any] | None:\n    if self.world_size == 1:\n        return tensor_dict\n    if self.rank_in_group == src:\n        assert isinstance(tensor_dict, dict), f'Expecting a dictionary, got {type(tensor_dict)}'\n        metadata_list, tensor_list = _split_tensor_dict(tensor_dict)\n    else:\n        metadata_list = None\n        tensor_list = []\n    recv_metadata_list: list[tuple[str, Any]] = self.tcp_store_group.broadcast_obj(metadata_list, src)\n    if self.rank_in_group != src:\n        tensor_dict = {}\n        for key, value in recv_metadata_list:\n            if isinstance(value, TensorMetadata):\n                tensor = torch.empty(value.size, dtype=value.dtype, device=value.device)\n                tensor_list.append(tensor)\n                tensor_dict[key] = tensor\n            else:\n                tensor_dict[key] = value\n    for tensor in tensor_list:\n        if tensor.numel() == 0:\n            continue\n        if self.device_communicator and tensor.is_cuda:\n            tensor.copy_(self.device_communicator.broadcast(tensor, src))\n        else:\n            tensor.copy_(self.tcp_store_group.broadcast(tensor, src))\n    return tensor_dict",
        "origin": "/tmp/vllm_repo/vllm/distributed/stateless_coordinator.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(tensor: torch.Tensor, group_name: str) -> torch.Tensor:\n    assert group_name in _groups, f'Group {group_name} is not found.'\n    group = _groups[group_name]()\n    if group is None:\n        raise ValueError(f'Group {group_name} is destroyed.')\n    return group._all_reduce_out_place(tensor)",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "all_reduce_fake",
        "coords": [
            27,
            16,
            8
        ],
        "fiber": 20,
        "logic": "def all_reduce_fake(tensor: torch.Tensor, group_name: str) -> torch.Tensor:\n    return torch.empty_like(tensor)",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "set_custom_all_reduce",
        "coords": [
            29,
            13,
            2
        ],
        "fiber": 13,
        "logic": "def set_custom_all_reduce(enable: bool):\n    global _ENABLE_CUSTOM_ALL_REDUCE\n    _ENABLE_CUSTOM_ALL_REDUCE = enable",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "init_distributed_environment",
        "coords": [
            27,
            5,
            26
        ],
        "fiber": 27,
        "logic": "def init_distributed_environment(world_size: int=-1, rank: int=-1, distributed_init_method: str='env://', local_rank: int=-1, backend: str='nccl', timeout: timedelta | None=None):\n    logger.debug('world_size=%d rank=%d local_rank=%d distributed_init_method=%s backend=%s', world_size, rank, local_rank, distributed_init_method, backend)\n    from vllm.config import get_current_vllm_config_or_none\n    config = get_current_vllm_config_or_none()\n    enable_elastic_ep = config is not None and config.parallel_config.enable_elastic_ep\n    if config is not None and config.parallel_config.distributed_executor_backend != 'external_launcher' and (config.parallel_config.nnodes > 1 or config.parallel_config.data_parallel_size > 1) and (not enable_elastic_ep):\n        parallel_config = config.parallel_config\n        rank = parallel_config.data_parallel_rank * world_size + rank\n        world_size = parallel_config.world_size_across_dp\n        if parallel_config.nnodes > 1:\n            ip = parallel_config.master_addr\n            port = parallel_config.master_port\n            distributed_init_method = get_distributed_init_method(ip, port)\n        else:\n            ip = parallel_config.data_parallel_master_ip\n            port = parallel_config.get_next_dp_init_port()\n            distributed_init_method = get_distributed_init_method(ip, port)\n            logger.debug('Adjusting world_size=%d rank=%d distributed_init_method=%s for DP', world_size, rank, distributed_init_method)\n    if not torch.distributed.is_initialized():\n        logger.info('world_size=%d rank=%d local_rank=%d distributed_init_method=%s backend=%s', world_size, rank, local_rank, distributed_init_method, backend)\n        assert distributed_init_method is not None, 'distributed_init_method must be provided when initializing distributed environment'\n        if not torch.distributed.is_backend_available(backend):\n            logger.warning('Distributed backend %s is not available; falling back to gloo.', backend)\n            assert torch.distributed.is_gloo_available(), 'Fallback Gloo backend is not available.'\n            backend = 'gloo'\n        torch.distributed.init_process_group(backend=backend, init_method=distributed_init_method, world_size=world_size, rank=rank, timeout=timeout)\n        if enable_elastic_ep:\n            tp_pp_cpu_group = torch.distributed.new_group(backend='gloo', timeout=timeout)\n            if _node_count(tp_pp_cpu_group) > 1:\n                raise RuntimeError('Elastic EP is not yet supported with multi-node TP/PP')\n    if local_rank == -1:\n        local_rank = envs.LOCAL_RANK if distributed_init_method == 'env://' else rank\n    global _WORLD, _NODE_COUNT, _INNER_DP_WORLD\n    if enable_elastic_ep:\n        _init_elastic_ep_world(config, local_rank, backend, rank, world_size)\n        return\n    if _WORLD is None:\n        ranks = list(range(torch.distributed.get_world_size()))\n        _WORLD = init_world_group(ranks, local_rank, backend)\n        if config is not None and config.parallel_config.nnodes > 1:\n            _NODE_COUNT = config.parallel_config.nnodes\n        else:\n            _NODE_COUNT = _node_count(_WORLD.cpu_group)\n        logger.debug('Detected %d nodes in the distributed environment', _NODE_COUNT)\n    else:\n        assert _WORLD.world_size == torch.distributed.get_world_size(), 'world group already initialized with a different world size'\n    if config is not None and config.parallel_config.nnodes_within_dp > 1:\n        if parallel_config.data_parallel_size > 1:\n            world_size_inner_dp = parallel_config.world_size\n            group_ranks = [[dp_rank * world_size_inner_dp + i for i in range(world_size_inner_dp)] for dp_rank in range(parallel_config.data_parallel_size)]\n            _INNER_DP_WORLD = init_model_parallel_group(group_ranks, get_world_group().local_rank, backend, use_message_queue_broadcaster=True, group_name='inner_dp_world', use_device_communicator=False)\n        else:\n            _INNER_DP_WORLD = _WORLD",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "destroy_distributed_environment",
        "coords": [
            28,
            16,
            15
        ],
        "fiber": 28,
        "logic": "def destroy_distributed_environment():\n    global _WORLD, _NODE_COUNT\n    if _WORLD:\n        _WORLD.destroy()\n    _WORLD = None\n    _NODE_COUNT = None\n    if torch.distributed.is_initialized():\n        torch.distributed.destroy_process_group()",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "cleanup_dist_env_and_memory",
        "coords": [
            23,
            29,
            19
        ],
        "fiber": 9,
        "logic": "def cleanup_dist_env_and_memory(shutdown_ray: bool=False):\n    envs.disable_envs_cache()\n    from vllm.platforms import current_platform\n    if current_platform.is_rocm():\n        from vllm._aiter_ops import rocm_aiter_ops\n        rocm_aiter_ops.refresh_env_variables()\n    gc.unfreeze()\n    destroy_model_parallel()\n    destroy_distributed_environment()\n    if shutdown_ray:\n        import ray\n        ray.shutdown()\n    gc.collect()\n    from vllm.platforms import current_platform\n    if not current_platform.is_cpu():\n        torch.accelerator.empty_cache()\n        try:\n            torch._C._host_emptyCache()\n        except AttributeError:\n            logger.warning('torch._C._host_emptyCache() only available in Pytorch >=2.5')",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "create_mq_broadcaster",
        "coords": [
            3,
            3,
            29
        ],
        "fiber": 4,
        "logic": "def create_mq_broadcaster(self, writer_rank=0, external_writer_handle=None, blocking=True):\n    from vllm.distributed.device_communicators.shm_broadcast import MessageQueue\n    return MessageQueue.create_from_process_group(self.cpu_group, 1 << 22, 6, writer_rank=writer_rank, external_writer_handle=external_writer_handle, blocking=blocking)",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "create_single_reader_mq_broadcasters",
        "coords": [
            26,
            12,
            24
        ],
        "fiber": 0,
        "logic": "def create_single_reader_mq_broadcasters(self, reader_rank_in_group=0, blocking=False):\n    from vllm.distributed.device_communicators.shm_broadcast import MessageQueue\n    return MessageQueue.create_from_process_group_single_reader(self.cpu_group, 1 << 22, 6, reader_rank=self.ranks[reader_rank_in_group], blocking=blocking)",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input_: torch.Tensor) -> torch.Tensor:\n    \"\"\"\n        User-facing all-reduce function before we actually call the\n        all-reduce operation.\n\n        We need this because Dynamo does not support passing an arbitrary\n        object (`self` in this case) to a custom op. We need to pass the\n         group name as a string, and then look up the group coordinator from\n         the group name, dispatch the all-reduce operation to the group\n         coordinator.\n\n        In addition, PyTorch custom ops do not support mutation or returning\n        a new tensor in the same op. So we always make the all-reduce operation\n        out-of-place.\n        \"\"\"\n    if self.world_size == 1:\n        return input_\n    if self.use_custom_op_call:\n        return torch.ops.vllm.all_reduce(input_, group_name=self.unique_name)\n    else:\n        return self._all_reduce_out_place(input_)",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "_all_reduce_out_place",
        "coords": [
            5,
            15,
            30
        ],
        "fiber": 19,
        "logic": "def _all_reduce_out_place(self, input_: torch.Tensor) -> torch.Tensor:\n    if self.device_communicator is None:\n        raise ValueError('No device communicator found')\n    return self.device_communicator.all_reduce(input_)",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, input_: torch.Tensor, src: int=0):\n    \"\"\"Broadcast the input tensor.\n        NOTE: `src` is the local rank of the source rank.\n        \"\"\"\n    assert src < self.world_size, f'Invalid src rank ({src})'\n    if self.world_size == 1:\n        return input_\n    torch.distributed.broadcast(input_, src=self.ranks[src], group=self.device_group)\n    return input_",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "broadcast_object",
        "coords": [
            25,
            30,
            29
        ],
        "fiber": 22,
        "logic": "def broadcast_object(self, obj: Any | None=None, src: int=0):\n    \"\"\"Broadcast the input object.\n        NOTE: `src` is the local rank of the source rank.\n        \"\"\"\n    assert src < self.world_size, f'Invalid src rank ({src})'\n    if self.world_size == 1:\n        return obj\n    if self.mq_broadcaster is not None:\n        assert src == 0, 'Message queue broadcaster only supports src=0'\n        return self.mq_broadcaster.broadcast_object(obj)\n    if self.rank_in_group == src:\n        torch.distributed.broadcast_object_list([obj], src=self.ranks[src], group=self.cpu_group)\n        return obj\n    else:\n        recv = [None]\n        torch.distributed.broadcast_object_list(recv, src=self.ranks[src], group=self.cpu_group)\n        return recv[0]",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "broadcast_object_list",
        "coords": [
            12,
            26,
            30
        ],
        "fiber": 6,
        "logic": "def broadcast_object_list(self, obj_list: list[Any], src: int=0, group: ProcessGroup | None=None):\n    \"\"\"Broadcast the input object list.\n        NOTE: `src` is the local rank of the source rank.\n        \"\"\"\n    assert src < self.world_size, f'Invalid src rank ({src})'\n    if self.world_size == 1:\n        return obj_list\n    torch.distributed.broadcast_object_list(obj_list, src=self.ranks[src], group=self.device_group)\n    return obj_list",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "broadcast_tensor_dict",
        "coords": [
            18,
            13,
            5
        ],
        "fiber": 5,
        "logic": "def broadcast_tensor_dict(self, tensor_dict: dict[str, torch.Tensor | Any] | None=None, src: int=0, group: ProcessGroup | None=None, metadata_group: ProcessGroup | None=None) -> dict[str, torch.Tensor | Any] | None:\n    \"\"\"Broadcast the input tensor dictionary.\n        NOTE: `src` is the local rank of the source rank.\n        \"\"\"\n    if not torch.distributed.is_initialized() or self.world_size == 1:\n        return tensor_dict\n    group = self.device_group\n    metadata_group = self.cpu_group\n    assert src < self.world_size, f'Invalid src rank ({src})'\n    rank_in_group = self.rank_in_group\n    if rank_in_group == src:\n        metadata_list: list[tuple[Any, Any]] = []\n        assert isinstance(tensor_dict, dict), f'Expecting a dictionary, got {type(tensor_dict)}'\n        metadata_list, tensor_list = _split_tensor_dict(tensor_dict)\n        self.broadcast_object(metadata_list, src=src)\n        async_handles = []\n        for tensor in tensor_list:\n            if tensor.numel() == 0:\n                continue\n            if tensor.is_cpu:\n                handle = torch.distributed.broadcast(tensor, src=self.ranks[src], group=metadata_group, async_op=True)\n            else:\n                handle = torch.distributed.broadcast(tensor, src=self.ranks[src], group=group, async_op=True)\n            async_handles.append(handle)\n        for async_handle in async_handles:\n            async_handle.wait()\n    else:\n        metadata_list = self.broadcast_object(None, src=src)\n        tensor_dict = {}\n        async_handles = []\n        for key, value in metadata_list:\n            if isinstance(value, TensorMetadata):\n                tensor = torch.empty(value.size, dtype=value.dtype, device=value.device)\n                if tensor.numel() == 0:\n                    tensor_dict[key] = tensor\n                    continue\n                if tensor.is_cpu:\n                    handle = torch.distributed.broadcast(tensor, src=self.ranks[src], group=metadata_group, async_op=True)\n                else:\n                    handle = torch.distributed.broadcast(tensor, src=self.ranks[src], group=group, async_op=True)\n                async_handles.append(handle)\n                tensor_dict[key] = tensor\n            else:\n                tensor_dict[key] = value\n        for async_handle in async_handles:\n            async_handle.wait()\n    return tensor_dict",
        "origin": "/tmp/vllm_repo/vllm/distributed/parallel_state.py"
    },
    {
        "id": "stateless_init_torch_distributed_process_group",
        "coords": [
            15,
            29,
            14
        ],
        "fiber": 27,
        "logic": "def stateless_init_torch_distributed_process_group(host: str, port: int, rank: int, world_size: int, backend: str, group_name: str | None=None, return_store: bool=False, listen_socket: socket.socket | None=None) -> ProcessGroup | tuple[ProcessGroup, Store]:\n    \"\"\"\n    A replacement for `torch.distributed.init_process_group` that does not\n    pollute the global state. The created ProcessGroup object can be used for\n    some operations such as `allreduce`, because it does not depend on the\n    global rank. However, some operations such as `broadcast` cannot be used\n    because it depends on the global rank.\n\n    # TODO: ask for help from PyTorch team if we need the `broadcast` operation.\n\n    This function is useful when we are not sure about the total number of\n    processes in the process group. For example, we may have process\n    1, 2, ..., 8 who want to communicate, and process 9 might be the same\n    process as process 1, or it might be a different process; process 10\n    might be the same process as process 5, or it might be a different process.\n    In this case, how can we reliably form a communication channel within\n    process 9 and 10, without affecting the communication channel within\n    process 1, 2, ..., 8?\n\n    One possible solution is to figure out if process 9 and 10 are the same\n    as process 1 and 5 beforehand, and then form a communication channel\n    based on the information, adjusting the ranks and world_size etc. However,\n    figuring out the information is not always easy, and it will interfere\n    with the main communication channel.\n\n    Our solution is to always form a communication channel with process 1, 2,\n    ..., 8, and then use this function to form another communication channel\n    with process 9 and 10. This way, regardless of whether process 9 and 10\n    are the same as process 1 and 5, the main communication channel is\n    always formed with process 1, 2, ..., 8, and the additional communication\n    channel is formed with process 9 and 10.\n\n    When *listen_socket* is provided, the rendezvous step\n    is skipped and a ``TCPStore`` server is created directly using the\n    pre-bound socket.  This is useful for eliminating TOCTOU races\n    between port allocation and binding.\n    \"\"\"\n    init_method = get_tcp_uri(host, port)\n    backend = Backend(backend)\n    timeout = _get_default_timeout(backend)\n    if listen_socket is not None:\n        store = create_tcp_store(host, port, listen_socket=listen_socket, world_size=world_size, is_master=True, timeout=timeout, multi_tenant=True)\n    else:\n        store, rank, world_size = next(rendezvous(init_method, rank, world_size, timeout=timeout))\n    store.set_timeout(timeout)\n    group_rank = rank\n    group_size = world_size\n    prefix_store = PrefixStore(init_method, store)\n    if backend == 'gloo':\n        pg = init_gloo_process_group(prefix_store=prefix_store, group_rank=group_rank, group_size=group_size, timeout=timeout)\n    else:\n        from vllm.platforms import current_platform\n        pg = current_platform.stateless_init_device_torch_dist_pg(backend=backend, prefix_store=prefix_store, group_rank=group_rank, group_size=group_size, timeout=timeout)\n    if group_name is not None:\n        from torch._C._distributed_c10d import _register_process_group\n        pg._set_group_name(group_name)\n        _register_process_group(group_name, pg)\n    if return_store:\n        return (pg, store)\n    else:\n        return pg",
        "origin": "/tmp/vllm_repo/vllm/distributed/utils.py"
    },
    {
        "id": "stateless_destroy_torch_distributed_process_group",
        "coords": [
            15,
            14,
            22
        ],
        "fiber": 20,
        "logic": "def stateless_destroy_torch_distributed_process_group(pg: ProcessGroup) -> None:\n    \"\"\"\n    Destroy ProcessGroup returned by\n        stateless_init_torch_distributed_process_group().\n    \"\"\"\n    pg.shutdown()\n    _unregister_process_group(pg.group_name)",
        "origin": "/tmp/vllm_repo/vllm/distributed/utils.py"
    },
    {
        "id": "broadcast_obj",
        "coords": [
            20,
            7,
            1
        ],
        "fiber": 28,
        "logic": "def broadcast_obj(self, obj: Any | None, src: int) -> Any:\n    \"\"\"Broadcast an object from a source rank to all other ranks.\n        It does not clean up after all ranks have received the object.\n        Use it for limited times, e.g., for initialization.\n        \"\"\"\n    if self.rank == src:\n        self.expire_data()\n        key = f'broadcast_from/{src}/{self.broadcast_send_counter}'\n        self.store.set(key, pickle.dumps(obj))\n        self.broadcast_send_counter += 1\n        self.entries.append((key, time.time()))\n        return obj\n    else:\n        key = f'broadcast_from/{src}/{self.broadcast_recv_src_counter[src]}'\n        recv_obj = pickle.loads(self.store.get(key))\n        self.broadcast_recv_src_counter[src] += 1\n        return recv_obj",
        "origin": "/tmp/vllm_repo/vllm/distributed/utils.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, tensor: torch.Tensor, src: int) -> torch.Tensor:\n    \"\"\"Broadcast a tensor from source rank to all other ranks.\"\"\"\n    if self.rank == src:\n        tensor_bytes = pickle.dumps(tensor)\n        self.expire_data()\n        key = f'broadcast_tensor/{src}/{self.broadcast_send_counter}'\n        self.store.set(key, tensor_bytes)\n        self.broadcast_send_counter += 1\n        self.entries.append((key, time.time()))\n        return tensor\n    else:\n        key = f'broadcast_tensor/{src}/{self.broadcast_recv_src_counter[src]}'\n        tensor = pickle.loads(self.store.get(key))\n        self.broadcast_recv_src_counter[src] += 1\n        return tensor",
        "origin": "/tmp/vllm_repo/vllm/distributed/utils.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, tensor: torch.Tensor, op=torch.distributed.ReduceOp.SUM) -> torch.Tensor:\n    \"\"\"All-reduce a tensor across all ranks.\"\"\"\n    tensors = self.all_gather_obj(tensor)\n    result = tensors[0].clone()\n    for t in tensors[1:]:\n        if op == torch.distributed.ReduceOp.SUM:\n            result.add_(t)\n        elif op == torch.distributed.ReduceOp.PRODUCT:\n            result.mul_(t)\n        elif op == torch.distributed.ReduceOp.MAX:\n            result = torch.maximum(result, t)\n        elif op == torch.distributed.ReduceOp.MIN:\n            result = torch.minimum(result, t)\n    return result",
        "origin": "/tmp/vllm_repo/vllm/distributed/utils.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input_):\n    if self.pynccl_comm is not None and should_nccl_symm_mem_allreduce(self.pynccl_comm.world_size, input_):\n        out = torch.ops.vllm.all_reduce_symmetric_with_copy(input_)\n        if out is not None:\n            return out\n    qr_comm = self.qr_comm\n    if qr_comm is not None and (not qr_comm.disabled) and qr_comm.should_quick_allreduce(input_):\n        out = qr_comm.quick_all_reduce(input_)\n        assert out is not None\n        return out\n    fi_ar_comm = self.fi_ar_comm\n    if fi_ar_comm is not None and (not fi_ar_comm.disabled) and fi_ar_comm.should_use_fi_ar(input_):\n        out = fi_ar_comm.all_reduce(input_)\n        assert out is not None\n        return out\n    ca_comm = self.ca_comm\n    if ca_comm is not None and (not ca_comm.disabled) and ca_comm.should_custom_ar(input_):\n        out = ca_comm.custom_all_reduce(input_)\n        assert out is not None\n        return out\n    symm_mem_comm = self.symm_mem_comm\n    if symm_mem_comm is not None and symm_mem_comm.should_use_symm_mem(input_):\n        out = symm_mem_comm.all_reduce(input_)\n        assert out is not None\n        return out\n    pynccl_comm = self.pynccl_comm\n    if pynccl_comm is None or pynccl_comm.disabled:\n        out = input_.clone()\n        torch.distributed.all_reduce(out, group=self.device_group)\n        return out\n    assert pynccl_comm is not None\n    out = pynccl_comm.all_reduce(input_)\n    if out is None:\n        out = input_.clone()\n        torch.distributed.all_reduce(out, group=self.device_group)\n    return out",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/cuda_communicator.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, tensor: torch.Tensor, src: int=0) -> torch.Tensor:\n    \"\"\"Broadcast a tensor from source rank to all ranks.\"\"\"\n    if self.world_size == 1:\n        return tensor\n    pynccl_comm = self.pynccl_comm\n    if pynccl_comm is not None and (not pynccl_comm.disabled):\n        pynccl_comm.broadcast(tensor, src)\n        return tensor\n    else:\n        raise ValueError('No PyNCCL communicator found')",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/cuda_communicator.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input_) -> torch.Tensor:\n    dist.all_reduce(input_, group=self.device_group)\n    return input_",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/xpu_communicator.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, input_: torch.Tensor, src: int=0) -> None:\n    dist.broadcast(input_, src=src, group=self.device_group)",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/xpu_communicator.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, inp: torch.Tensor, *, out: torch.Tensor | None=None) -> torch.Tensor | None:\n    if not self.should_use_symm_mem(inp):\n        return None\n    if out is None:\n        out = torch.empty_like(inp)\n    self.buffer[:inp.numel()].copy_(inp.view(-1))\n    use_multimem = False\n    if self.force_multimem is not None:\n        use_multimem = self.force_multimem\n    else:\n        use_multimem = self.world_size in self._WORLD_SIZES_MULTIMEM[self.device_capability]\n    if use_multimem:\n        torch.ops.symm_mem.multimem_all_reduce_(self.buffer[:inp.numel()], 'sum', self.group.group_name)\n    else:\n        torch.ops.symm_mem.two_shot_all_reduce_(self.buffer[:inp.numel()], 'sum', self.group.group_name)\n    out.copy_(self.buffer[:inp.numel()].view(out.shape))\n    return out",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/symm_mem.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, inp: torch.Tensor, *, out: torch.Tensor=None, registered: bool=False):\n    \"\"\"Performs an out-of-place all reduce.\n\n        If registered is True, this assumes inp's pointer is already\n        IPC-registered. Otherwise, inp is first copied into a pre-registered\n        buffer.\n        \"\"\"\n    if out is None:\n        out = torch.empty_like(inp)\n    if registered:\n        ops.all_reduce(self._ptr, inp, out, 0, 0)\n    else:\n        ops.all_reduce(self._ptr, inp, out, self.buffer_ptrs[self.rank], self.max_size)\n    return out",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/custom_all_reduce.py"
    },
    {
        "id": "custom_all_reduce",
        "coords": [
            14,
            2,
            10
        ],
        "fiber": 26,
        "logic": "def custom_all_reduce(self, input: torch.Tensor) -> torch.Tensor | None:\n    \"\"\"The main allreduce API that provides support for cuda graph.\"\"\"\n    if self.disabled or not self.should_custom_ar(input):\n        return None\n    if self._IS_CAPTURING:\n        if torch.cuda.is_current_stream_capturing():\n            return self.all_reduce(input, registered=True)\n        else:\n            return torch.empty_like(input)\n    else:\n        return self.all_reduce(input, registered=False)",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/custom_all_reduce.py"
    },
    {
        "id": "init_quick_all_reduce",
        "coords": [
            13,
            29,
            29
        ],
        "fiber": 9,
        "logic": "def init_quick_all_reduce(self):\n    self.use_fp16_kernels = envs.VLLM_ROCM_QUICK_REDUCE_CAST_BF16_TO_FP16\n    regime_str = envs.VLLM_ROCM_QUICK_REDUCE_QUANTIZATION\n    if regime_str not in QuickReduceRegime.__members__:\n        logger.warning('Custom quick allreduce:', f'Invalid quantization level: {regime_str}. Supported levels: {list(QuickReduceRegime.__members__.keys())}')\n        return\n    if regime_str == 'NONE':\n        logger.debug(\"Custom quick allreduce is disabled based on env variable VLLM_ROCM_QUICK_REDUCE_QUANTIZATION='NONE'\")\n        return\n    self.qr_quant_level = QuickReduceRegime[regime_str]\n    vllm_config = get_current_vllm_config_or_none()\n    if vllm_config is not None and hasattr(vllm_config, 'model_config') and hasattr(vllm_config.model_config, 'dtype'):\n        dtype = vllm_config.model_config.dtype\n        if dtype not in [torch.float16, torch.bfloat16]:\n            logger.debug('Custom quick allreduce disabled: only supports float16 and float16, but get %s.', dtype)\n            return\n        if dtype == torch.bfloat16 and self.use_fp16_kernels:\n            logger.info('Custom quick allreduce: BF16 inputs will be converted to FP16 to improve performance. set envs.VLLM_ROCM_QUICK_REDUCE_CAST_BF16_TO_FP16=0 to turn off.')\n    qr_max_size = envs.VLLM_ROCM_QUICK_REDUCE_MAX_SIZE_BYTES_MB\n    if qr_max_size is not None:\n        if qr_max_size < 1:\n            logger.info('You should not set a max_size smaller than 1MB, which can lead to error or degradation to custom allreduce or rccl.')\n        qr_max_size = qr_max_size * MB\n    self._ptr = ops.init_custom_qr(self.rank, self.world_size, qr_max_size)\n    self.qr_max_size = qr_max_size if qr_max_size is not None else ops.qr_max_size()\n    self.create_shared_buffer()\n    self.disabled = False",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/quick_all_reduce.py"
    },
    {
        "id": "quick_all_reduce",
        "coords": [
            16,
            5,
            25
        ],
        "fiber": 15,
        "logic": "def quick_all_reduce(self, inp: torch.Tensor, *, out: torch.Tensor=None):\n    \"\"\"Performs an out-of-place custom quick all reduce.\"\"\"\n    if out is None:\n        out = torch.empty_like(inp)\n    ops.qr_all_reduce(self._ptr, inp, out, self.qr_quant_level.value, self.use_fp16_kernels)\n    return out",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/quick_all_reduce.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input_tensor: torch.Tensor) -> torch.Tensor:\n    _, hidden_dim = input_tensor.shape\n    workspace = get_fi_ar_workspace(world_size=self.world_size, rank=self.rank, max_token_num=self.max_num_tokens, hidden_dim=hidden_dim, dtype=input_tensor.dtype, group=self.group)\n    return flashinfer_comm.allreduce_fusion(input=input_tensor, workspace=workspace, pattern=flashinfer_comm.AllReduceFusionPattern.kAllReduce)",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/flashinfer_all_reduce.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input_: torch.Tensor) -> torch.Tensor:\n    dist.all_reduce(input_, group=self.device_group)\n    return input_",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/base_device_communicator.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, tensor: torch.Tensor, src: int=0) -> torch.Tensor:\n    \"\"\"Broadcast a tensor from source rank to all ranks.\"\"\"\n    if self.world_size == 1:\n        return tensor\n    torch.distributed.broadcast(tensor, self.ranks[src], self.device_group)\n    return tensor",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/base_device_communicator.py"
    },
    {
        "id": "all_reduce_symmetric_with_copy_impl",
        "coords": [
            16,
            8,
            10
        ],
        "fiber": 3,
        "logic": "def all_reduce_symmetric_with_copy_impl(input_tensor: torch.Tensor) -> torch.Tensor:\n    with nccl_symm_mem_context(pynccl_comm):\n        symm_input = torch.empty_like(input_tensor)\n        symm_output = torch.empty_like(input_tensor)\n    symm_input.copy_(input_tensor)\n    symm_output = pynccl_comm.all_reduce(symm_input, symm_output)\n    return symm_output",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/pynccl.py"
    },
    {
        "id": "all_reduce_symmetric_with_copy_fake",
        "coords": [
            23,
            7,
            9
        ],
        "fiber": 8,
        "logic": "def all_reduce_symmetric_with_copy_fake(input_tensor: torch.Tensor) -> torch.Tensor:\n    return torch.empty_like(input_tensor)",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/pynccl.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, in_tensor: torch.Tensor, out_tensor: torch.Tensor=None, op: ReduceOp=ReduceOp.SUM, stream=None) -> torch.Tensor:\n    if self.disabled:\n        return None\n    assert in_tensor.device == self.device, f'this nccl communicator is created to work on {self.device}, but the input tensor is on {in_tensor.device}'\n    if out_tensor is None:\n        out_tensor = torch.empty_like(in_tensor)\n    if stream is None:\n        stream = current_stream()\n    self.nccl.ncclAllReduce(buffer_type(in_tensor.data_ptr()), buffer_type(out_tensor.data_ptr()), in_tensor.numel(), ncclDataTypeEnum.from_torch(in_tensor.dtype), ncclRedOpTypeEnum.from_torch(op), self.comm, cudaStream_t(stream.cuda_stream))\n    return out_tensor",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/pynccl.py"
    },
    {
        "id": "broadcast",
        "coords": [
            27,
            24,
            29
        ],
        "fiber": 18,
        "logic": "def broadcast(self, tensor: torch.Tensor, src: int, stream=None):\n    if self.disabled:\n        return\n    assert tensor.device == self.device, f'this nccl communicator is created to work on {self.device}, but the input tensor is on {tensor.device}'\n    if stream is None:\n        stream = current_stream()\n    if src == self.rank:\n        sendbuff = buffer_type(tensor.data_ptr())\n        recvbuff = buffer_type(tensor.data_ptr())\n    else:\n        sendbuff = buffer_type()\n        recvbuff = buffer_type(tensor.data_ptr())\n    self.nccl.ncclBroadcast(sendbuff, recvbuff, tensor.numel(), ncclDataTypeEnum.from_torch(tensor.dtype), src, self.comm, cudaStream_t(stream.cuda_stream))",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/pynccl.py"
    },
    {
        "id": "broadcast_object",
        "coords": [
            25,
            30,
            29
        ],
        "fiber": 22,
        "logic": "def broadcast_object(self, obj=None):\n    if self._is_writer:\n        self.enqueue(obj)\n        return obj\n    return self.dequeue()",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/shm_broadcast.py"
    },
    {
        "id": "ncclBroadcast",
        "coords": [
            27,
            1,
            29
        ],
        "fiber": 26,
        "logic": "def ncclBroadcast(self, sendbuff: buffer_type, recvbuff: buffer_type, count: int, datatype: int, root: int, comm: ncclComm_t, stream: cudaStream_t) -> None:\n    self.NCCL_CHECK(self._funcs['ncclBroadcast'](sendbuff, recvbuff, count, datatype, root, comm, stream))",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/pynccl_wrapper.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input_):\n    self.dist_module.all_reduce(input_, group=self.device_group)\n    return input_",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/cpu_communicator.py"
    },
    {
        "id": "all_reduce",
        "coords": [
            18,
            4,
            10
        ],
        "fiber": 1,
        "logic": "def all_reduce(self, input: torch.Tensor, group: ProcessGroup | None=None) -> None:\n    torch.ops._C.shm_allreduce(self.handle, input)",
        "origin": "/tmp/vllm_repo/vllm/distributed/device_communicators/cpu_communicator.py"
    },
    {
        "id": "packed_broadcast_producer",
        "coords": [
            4,
            24,
            11
        ],
        "fiber": 8,
        "logic": "def packed_broadcast_producer(iterator: Iterator[tuple[str, torch.Tensor]], group: Any, src: int, post_iter_func: Callable[[tuple[str, torch.Tensor]], torch.Tensor], buffer_size_bytes: int=DEFAULT_PACKED_BUFFER_SIZE_BYTES, num_buffers: int=DEFAULT_PACKED_NUM_BUFFERS) -> None:\n    \"\"\"Broadcast tensors in a packed manner from trainer to workers.\n\n    Args:\n        iterator: Iterator of model parameters. Returns a tuple of (name, tensor)\n        group: Process group (PyNcclCommunicator)\n        src: Source rank (0 in current implementation)\n        post_iter_func: Function to apply to each (name, tensor) pair before\n                       packing, should return a tensor\n        buffer_size_bytes: Size in bytes for each packed tensor buffer.\n                          Both producer and consumer must use the same value.\n        num_buffers: Number of buffers for double/triple buffering.\n                    Both producer and consumer must use the same value.\n\n    \"\"\"\n    target_packed_tensor_size = buffer_size_bytes\n    streams = [torch.cuda.Stream() for _ in range(num_buffers)]\n    buffer_idx = 0\n    packing_tensor_list: list[list[torch.Tensor]] = [[] for _ in range(num_buffers)]\n    packing_tensor_sizes: list[int] = [0 for _ in range(num_buffers)]\n    packed_tensors: list[torch.Tensor] = [torch.empty(0, dtype=torch.uint8, device='cuda') for _ in range(num_buffers)]\n    while True:\n        streams[buffer_idx].synchronize()\n        with torch.cuda.stream(streams[buffer_idx]):\n            try:\n                packing_tensor_list[buffer_idx] = []\n                packing_tensor_sizes[buffer_idx] = 0\n                while True:\n                    tensor = post_iter_func(next(iterator)).contiguous().view(torch.uint8).view(-1)\n                    packing_tensor_list[buffer_idx].append(tensor)\n                    packing_tensor_sizes[buffer_idx] += tensor.numel()\n                    if packing_tensor_sizes[buffer_idx] > target_packed_tensor_size:\n                        break\n                packed_tensors[buffer_idx] = torch.cat(packing_tensor_list[buffer_idx], dim=0)\n                group.broadcast(packed_tensors[buffer_idx], src=src)\n                buffer_idx = (buffer_idx + 1) % num_buffers\n            except StopIteration:\n                if len(packing_tensor_list[buffer_idx]) > 0:\n                    packed_tensors[buffer_idx] = torch.cat(packing_tensor_list[buffer_idx], dim=0)\n                    group.broadcast(packed_tensors[buffer_idx], src=src)\n                break",
        "origin": "/tmp/vllm_repo/vllm/distributed/weight_transfer/packed_tensor.py"
    },
    {
        "id": "packed_broadcast_consumer",
        "coords": [
            21,
            21,
            7
        ],
        "fiber": 18,
        "logic": "def packed_broadcast_consumer(iterator: Iterator[tuple[str, tuple[list[int], torch.dtype]]], group: Any, src: int, post_unpack_func: Callable[[list[tuple[str, torch.Tensor]]], None], buffer_size_bytes: int=DEFAULT_PACKED_BUFFER_SIZE_BYTES, num_buffers: int=DEFAULT_PACKED_NUM_BUFFERS) -> None:\n    \"\"\"Consume packed tensors and unpack them into a list of tensors.\n\n    Args:\n        iterator: Iterator of parameter metadata. Returns (name, (shape, dtype))\n        group: Process group (PyNcclCommunicator)\n        src: Source rank (0 in current implementation)\n        post_unpack_func: Function to apply to each list of (name, tensor) after\n                         unpacking\n        buffer_size_bytes: Size in bytes for each packed tensor buffer.\n                          Both producer and consumer must use the same value.\n        num_buffers: Number of buffers for double/triple buffering.\n                    Both producer and consumer must use the same value.\n\n    \"\"\"\n\n    def unpack_tensor(packed_tensor: torch.Tensor, names: list[str], shapes: list[list[int]], dtypes: list[torch.dtype], tensor_sizes: list[int]) -> list[tuple[str, torch.Tensor]]:\n        \"\"\"Unpack a single tensor into a list of tensors.\n\n        Args:\n            packed_tensor: The packed torch.uint8 tensor to unpack\n            names: List of tensor names\n            shapes: List of tensor shapes\n            dtypes: List of tensor dtypes\n            tensor_sizes: List of tensor sizes in bytes\n\n        Returns:\n            unpacked List[(name, tensor)]\n        \"\"\"\n        unpacked_tensors = packed_tensor.split(tensor_sizes)\n        unpacked_list = [(name, tensor.contiguous().view(dtype).view(*shape)) for name, shape, dtype, tensor in zip(names, shapes, dtypes, unpacked_tensors)]\n        return unpacked_list\n    target_packed_tensor_size = buffer_size_bytes\n    streams = [torch.cuda.Stream() for _ in range(num_buffers)]\n    buffer_idx = 0\n    packing_tensor_meta_data: list[list[tuple[str, list[int], torch.dtype, int]]] = [[] for _ in range(num_buffers)]\n    packing_tensor_sizes: list[int] = [0 for _ in range(num_buffers)]\n    packed_tensors: list[torch.Tensor] = [torch.empty(0, dtype=torch.uint8, device='cuda') for _ in range(num_buffers)]\n    while True:\n        streams[buffer_idx].synchronize()\n        with torch.cuda.stream(streams[buffer_idx]):\n            packing_tensor_meta_data[buffer_idx] = []\n            packing_tensor_sizes[buffer_idx] = 0\n            try:\n                while True:\n                    name, (shape, dtype) = next(iterator)\n                    tensor_size = math.prod(shape) * dtype.itemsize\n                    packing_tensor_meta_data[buffer_idx].append((name, shape, dtype, tensor_size))\n                    packing_tensor_sizes[buffer_idx] += tensor_size\n                    if packing_tensor_sizes[buffer_idx] > target_packed_tensor_size:\n                        break\n                packed_tensors[buffer_idx] = torch.empty(packing_tensor_sizes[buffer_idx], dtype=torch.uint8, device='cuda')\n                group.broadcast(packed_tensors[buffer_idx], src=src)\n                names, shapes, dtypes, tensor_sizes = zip(*packing_tensor_meta_data[buffer_idx])\n                post_unpack_func(unpack_tensor(packed_tensors[buffer_idx], list(names), list(shapes), list(dtypes), list(tensor_sizes)))\n                buffer_idx = (buffer_idx + 1) % num_buffers\n            except StopIteration:\n                if len(packing_tensor_meta_data[buffer_idx]) > 0:\n                    packed_tensors[buffer_idx] = torch.empty(packing_tensor_sizes[buffer_idx], dtype=torch.uint8, device='cuda')\n                    group.broadcast(packed_tensors[buffer_idx], src=src)\n                    names, shapes, dtypes, tensor_sizes = zip(*packing_tensor_meta_data[buffer_idx])\n                    post_unpack_func(unpack_tensor(packed_tensors[buffer_idx], list(names), list(shapes), list(dtypes), list(tensor_sizes)))\n                break",
        "origin": "/tmp/vllm_repo/vllm/distributed/weight_transfer/packed_tensor.py"
    },
    {
        "id": "_sync_block_size_with_kernel",
        "coords": [
            30,
            18,
            8
        ],
        "fiber": 25,
        "logic": "def _sync_block_size_with_kernel(self) -> None:\n    backends = get_current_attn_backends(self.vllm_config)\n    kernel_block_size = select_common_block_size(self.block_size, backends)\n    self._logical_num_blocks = self.num_blocks\n    if self.block_size != kernel_block_size:\n        logger.info_once('User-specified logical block size (%s) does not match physical kernel block size (%s). Using the latter.', self.block_size, kernel_block_size)\n        assert self.block_size > kernel_block_size\n        self._physical_blocks_per_logical_kv_block = self.block_size // kernel_block_size\n        self.block_size = kernel_block_size\n        self._block_size[self.engine_id] = kernel_block_size\n        self.num_blocks *= self._physical_blocks_per_logical_kv_block",
        "origin": "/tmp/vllm_repo/vllm/distributed/kv_transfer/kv_connector/v1/nixl_connector.py"
    },
    {
        "id": "_logical_to_kernel_block_ids",
        "coords": [
            29,
            23,
            27
        ],
        "fiber": 17,
        "logic": "def _logical_to_kernel_block_ids(self, block_ids: BlockIds) -> BlockIds:\n    \"\"\"\n        Convert logical block ids to kernel physical block ids.\n        This is required when the logical block size (the one set by the user)\n        does not match the one required by the attn backend.\n        \"\"\"\n    if self._physical_blocks_per_logical_kv_block == 1:\n        return block_ids\n    block_arange = np.arange(0, self._physical_blocks_per_logical_kv_block).reshape(1, -1)\n    group_specs = self.kv_cache_config.kv_cache_groups\n    return [BlockTable.map_to_kernel_blocks(np.array(group), self._physical_blocks_per_logical_kv_block, block_arange).tolist() if not isinstance(group_specs[i].kv_cache_spec, MambaSpec) else group for i, group in enumerate(block_ids)]",
        "origin": "/tmp/vllm_repo/vllm/distributed/kv_transfer/kv_connector/v1/nixl_connector.py"
    },
    {
        "id": "create_scheduler_adapter",
        "coords": [
            11,
            2,
            22
        ],
        "fiber": 4,
        "logic": "def create_scheduler_adapter(server_url: str, zmq_context: zmq.Context, vllm_config: VllmConfig, mq_timeout: float, heartbeat_interval: float) -> LMCacheMPSchedulerAdapter:\n    world_size, kv_rank = extract_world_size_and_kv_rank(vllm_config.parallel_config.world_size, vllm_config.parallel_config.rank, vllm_config)\n    tp_size = vllm_config.parallel_config.tensor_parallel_size\n    kwargs: dict[str, Any] = {}\n    if _adapter_accepts_tp_size():\n        kwargs['tp_size'] = tp_size\n    return LMCacheMPSchedulerAdapter(server_url, zmq_context, vllm_config.model_config.model, world_size, kv_rank, vllm_config.cache_config.block_size, mq_timeout=mq_timeout, heartbeat_interval=heartbeat_interval, **kwargs)",
        "origin": "/tmp/vllm_repo/vllm/distributed/kv_transfer/kv_connector/v1/lmcache_mp_connector.py"
    },
    {
        "id": "increase_num_scheduled_tokens",
        "coords": [
            0,
            13,
            8
        ],
        "fiber": 21,
        "logic": "def increase_num_scheduled_tokens(self, num_new_tokens: int):\n    self.num_scheduled_tokens += num_new_tokens",
        "origin": "/tmp/vllm_repo/vllm/distributed/kv_transfer/kv_connector/v1/lmcache_mp_connector.py"
    },
    {
        "id": "schedule_write",
        "coords": [
            17,
            22,
            5
        ],
        "fiber": 13,
        "logic": "def schedule_write(self, task: WriteTask) -> None:\n    \"\"\"Schedule a write task.\n\n        Args:\n            task: The write task to schedule\n        \"\"\"\n    self.ensure_worker_started()\n    self._write_task_q.put(task)",
        "origin": "/tmp/vllm_repo/vllm/distributed/kv_transfer/kv_connector/v1/moriio/moriio_engine.py"
    },
    {
        "id": "schedule_write_blocks",
        "coords": [
            19,
            29,
            28
        ],
        "fiber": 14,
        "logic": "def schedule_write_blocks(self, request_id: ReqId, transfer_id: TransferId, dst_engine_id: str, local_block_ids: list[int], remote_block_ids: list[int] | None, layer_name: str, kv_layer: torch.Tensor, remote_notify_port: int, remote_ip: str) -> None:\n    \"\"\"Schedule a block write operation.\n\n        Args:\n            request_id: Unique identifier for the request\n            transfer_id: Unique identifier for the transfer\n            dst_engine_id: Destination engine ID\n            local_block_ids: Local block IDs to transfer\n            remote_block_ids: Hint for remote block IDs\n            layer_name: Name of the layer\n            kv_layer: KV cache tensor\n            remote_notify_port: Port for completion notification\n            remote_ip: IP address of remote node\n        \"\"\"\n    stream = torch.cuda.current_stream()\n    event = torch.cuda.Event()\n    event.record(stream)\n    task = WriteTask(request_id=request_id, transfer_id=transfer_id, dst_engine_id=dst_engine_id, local_block_ids=local_block_ids, remote_block_ids_hint=remote_block_ids, layer_name=layer_name, event=event, remote_notify_port=remote_notify_port, remote_ip=remote_ip)\n    self._writer.schedule_write(task)",
        "origin": "/tmp/vllm_repo/vllm/distributed/kv_transfer/kv_connector/v1/moriio/moriio_connector.py"
    },
    {
        "id": "broadcast_expert_mapping",
        "coords": [
            1,
            0,
            12
        ],
        "fiber": 13,
        "logic": "def broadcast_expert_mapping(physical_to_logical: torch.Tensor | None, num_local_physical_experts: int | None, num_logical_experts: int | None, dp_group: StatelessGroupCoordinator, device: torch.device, src_rank: int=0) -> tuple[torch.Tensor, int, int]:\n    if dp_group.rank_in_group == src_rank:\n        assert physical_to_logical is not None\n        assert num_local_physical_experts is not None\n        assert num_logical_experts is not None\n        assert physical_to_logical.dtype == torch.int64\n        shape_tensor = torch.tensor(list(physical_to_logical.shape), dtype=torch.int64, device='cpu')\n        metadata_tensor = torch.tensor([num_local_physical_experts, num_logical_experts], dtype=torch.int64, device='cpu')\n    else:\n        shape_tensor = torch.empty(2, dtype=torch.int64, device='cpu')\n        metadata_tensor = torch.empty(2, dtype=torch.int64, device='cpu')\n    shape_tensor = dp_group.tcp_store_group.broadcast(shape_tensor, src_rank)\n    metadata_tensor = dp_group.tcp_store_group.broadcast(metadata_tensor, src_rank)\n    if dp_group.rank_in_group != src_rank:\n        assert device is not None\n        physical_to_logical = torch.empty(tuple(shape_tensor.tolist()), dtype=torch.int64, device=device)\n    assert physical_to_logical is not None\n    physical_to_logical = dp_group.broadcast(physical_to_logical, src_rank)\n    num_local_physical_experts = int(metadata_tensor[0].item())\n    num_logical_experts = int(metadata_tensor[1].item())\n    return (physical_to_logical, num_local_physical_experts, num_logical_experts)",
        "origin": "/tmp/vllm_repo/vllm/distributed/elastic_ep/elastic_execute.py"
    },
    {
        "id": "broadcast_expert_mapping",
        "coords": [
            1,
            0,
            12
        ],
        "fiber": 13,
        "logic": "def broadcast_expert_mapping(self) -> None:\n    standby_dp_group = get_standby_dp_group()\n    assert standby_dp_group is not None\n    model_config = self.worker.model_runner.model_config\n    eplb_state = self.worker.model_runner.eplb_state\n    assert eplb_state is not None\n    eplb_model_state = eplb_state.model_states[model_config.compute_hash()]\n    physical_to_logical = eplb_model_state.physical_to_logical_map\n    num_physical_experts = physical_to_logical.shape[1]\n    num_local_physical_experts = num_physical_experts // get_ep_group().world_size\n    num_logical_experts = eplb_model_state.logical_replica_count.shape[1]\n    broadcast_expert_mapping(physical_to_logical=physical_to_logical, num_local_physical_experts=num_local_physical_experts, num_logical_experts=num_logical_experts, dp_group=standby_dp_group, src_rank=0, device=self.worker.device)",
        "origin": "/tmp/vllm_repo/vllm/distributed/elastic_ep/elastic_execute.py"
    }
]
