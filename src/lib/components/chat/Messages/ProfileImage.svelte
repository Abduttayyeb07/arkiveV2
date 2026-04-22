<script lang="ts">
	import { ARKIVE_BASE_URL } from '$lib/constants';

	export let className = 'size-8';
	export let src = `${ARKIVE_BASE_URL}/static/logo.png`;
</script>

<img
	aria-hidden="true"
	src={src === ''
		? `${ARKIVE_BASE_URL}/static/favicon.png`
		: src.startsWith(ARKIVE_BASE_URL) ||
			  src.startsWith('https://www.gravatar.com/avatar/') ||
			  src.startsWith('data:') ||
			  src.startsWith('/')
			? src
			: `${ARKIVE_BASE_URL}/user.png`}
	class=" {className} object-cover rounded-full"
	alt="profile"
	draggable="false"
/>
